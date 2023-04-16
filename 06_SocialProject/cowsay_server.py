import asyncio
import cowsay

clients = {}
clients_names = {}
available_names = cowsay.list_cows()

async def chat(reader, writer):
    global clients
    global clients_names
    global available_names
    me = "{}:{}".format(*writer.get_extra_info('peername'))
    print(f"{me} appeared")
    my_name = ''
    clients[me] = asyncio.Queue()
    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(clients[me].get())
    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive],
                                           return_when=asyncio.FIRST_COMPLETED)
        try:
            for q in done:
                if q is send:
                    send = asyncio.create_task(reader.readline())
                    command = q.result().decode()
                    if len(command) == 0:
                        continue
                    print(command.strip())
                    if command[0] == ' ':
                        response_start_with = ' '
                        command = command[1:]
                    else:
                        response_start_with, command = command.split(maxsplit=1)
                        response_start_with += ' '
                    command = command.split(maxsplit=1)
                    match command:
                        case ["who"]:
                            await clients[me].put(response_start_with + ' '.join(clients_names.keys()))
                        case ["cows"]:
                            await clients[me].put(response_start_with + ' '.join(available_names))
                        case ["login", other]:
                            cow_name = other.strip()
                            if cow_name in available_names:
                                if my_name != '':
                                    available_names += [my_name]
                                    del clients_names[my_name]
                                clients_names[cow_name] = me
                                my_name = cow_name
                                available_names.remove(cow_name)
                                print(f'{me} is logined as {my_name}')
                                await clients[me].put(response_start_with +
                                                      f'You are logined as {my_name}')
                            else:
                                await clients[me].put(response_start_with + 'Name is not available')
                        case ['say', other]:
                            if my_name == '':
                                await clients[me].put(response_start_with + 'You are not authorized')
                            else:
                                cow_name, message = other.split(maxsplit=1)
                                if cow_name not in clients_names:
                                    await clients[clients_names[cow_name]].put(response_start_with +
                                                                               'No such cow')
                                else:
                                    message = cowsay.cowsay(message, cow=my_name)
                                    await clients[clients_names[cow_name]].put(' ' + message)
                        case ['yield', message]:
                            if my_name == '':
                                await clients[me].put(response_start_with + 'You are not authorized')
                            else:
                                message = cowsay.cowsay(message, cow=my_name)
                                for client in clients.values():
                                    if client is not clients[me]:
                                        await client.put(' ' + message)
                        case ['quit']:
                            available_names += [my_name]
                            del clients_names[my_name]
                            my_name = ''
                            print(f'{me} logined out')
                            await clients[me].put(response_start_with + 'Logined out')
                elif q is receive:
                    receive = asyncio.create_task(clients[me].get())
                    writer.write(f"{q.result()}\n".encode())
                    await writer.drain()
        except Exception as ex:
            print(ex)
    send.cancel()
    receive.cancel()
    print(me, "DONE")
    del clients[me]
    if my_name != '':
        available_names += [my_name]
        del clients_names[my_name]
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Server down')
