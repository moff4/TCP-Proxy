#!/usr/bin/env python3

import sys
import asyncio


HELP_MSG = '''
Simple TCP proxy
flags:
    --help, -h, -? - see this msg again
    --version, -v - print version
    --host, -H - destination host
    --post, -P - destination port
    --listen, -l - port to listen to (default: 8888)
    --buffer-limit - size of buffer for readers
'''


def check_cli():
    args = set(sys.argv)
    if {'-v', '--version'} & args:
        print('1.0')
        exit(0)
    elif {'-h', '--help', '-?'} & args:
        print(HELP_MSG)
        exit(0)


def get_cli_arg(*flags, default=None):
    try:
        return next(
            '='.join(arg.split('=')[1:])
            for arg in sys.argv
            if any(
                arg.startswith(x)
                for x in flags
            )
        )
    except StopIteration:
        return default


check_cli()

HOST = get_cli_arg('--host', '-H')
if HOST is None:
    print('--host not passed')
    exit(1)
PORT = get_cli_arg('--port', '-P')
if PORT is None:
    print('--port not passed')
    exit(1)
else:
    PORT = int(PORT)
LISTEN_PORT = int(get_cli_arg('--listen', '-l', default='8888'))
LIMIT = get_cli_arg('--buffer-limit')
if LIMIT is not None:
    LIMIT = int(LIMIT)


async def callback(client_reader, client_writer):
    async def proxy(reader, writer):
        async def close():
            try:
                await writer.drain()
            except Exception:
                ...
            try:
                writer.close()
            except Exception:
                ...
        try:
            while not (reader.at_eof() or writer.is_closing()):
                d = await reader.read(2 ** 8)
                writer.write(d)
            else:
                if writer.can_write_eof():
                    writer.write_eof()
                await close()
        except Exception:
            await close()
    server_reader, server_writer = await asyncio.open_connection(
        host=HOST,
        port=PORT,
        **({'limit': LIMIT} if LIMIT else {}),
    )
    tasks = [
        asyncio.create_task(proxy(server_reader, client_writer)),
        asyncio.create_task(proxy(client_reader, server_writer)),
    ]
    while not all(t.done() for t in tasks):
        await asyncio.sleep(1.0)


async def main():
    server = await asyncio.start_server(
        callback,
        host='127.0.0.1',
        port=LISTEN_PORT,
        **({'limit': LIMIT} if LIMIT else {}),
    )

    async with server:
        await server.serve_forever()

try:
    asyncio.run(main())
except KeyboardInterrupt:
    ...
