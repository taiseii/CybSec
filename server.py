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
                 `.........||||                    ,||||
                  .;.......||||               _.-!!|||||
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


Async server + CLI for reverse shells
Allows Speedy-J2 clients to connect and receive commands
"""

import asyncio
import socket

# CLI imports
#from prompt_toolkit import print_formatted_text as print, HTML, prompt
#from prompt_toolkit.styles import Style
#from prompt_toolkit.eventloop.defaults import use_asyncio_event_loop
#from prompt_toolkit.patch_stdout import patch_stdout
#from prompt_toolkit.shortcuts import print_container
#from prompt_toolkit.widgets import Frame, TextArea

#style = Style.from_dict({'ip': '#ff0066 underline',
#                         'status': '#44ff00 bold',
#                         })


# This is a (native) coroutine, 3.5> syntax
async def handle_marco(reader, writer):
    # Coroutine objects returned from async def functions are 'awaitable'
    # Go let something else run until whenever reader.read() is ready
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print("Received {} from {}".format(message, addr))

    print("Sending: {}".format(message))

    writer.write("Polo".encode())
    await writer.drain()

    print("Closing client socket")
    writer.close()

loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_marco, '127.0.0.1', 8888, loop=loop)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()



#if __name__ == '__main__':
#    Server()
#    print(HTML('<h1>Welcome to SPEEDY-J2</h1>'))
#    print(HTML('<ip>Hello</ip> <status>world</status>'), style=serverstyle)
#    nclient = prompt("Select a client (1-{}) to connect to: ".format(len(target_addresses)))
