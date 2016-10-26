import asyncio
import websockets
import multiprocessing
import json
import redis
import types
import signal
from motionweb import utils

listeners = set()

def new_video_handler(msg):
    filename = msg['data']
    print('Data received: {}'.format(filename))
    video = utils.video_to_dict(filename)
    obj = json.dumps(video)
    print('Data sent: {}'.format(obj))
    for l in listeners:
        asyncio.ensure_future(l.send(obj))

async def setup_redis(loop, stop_app):
    rd = redis.StrictRedis(decode_responses=True)
    ps = rd.pubsub(ignore_subscribe_messages=True)
    ps.subscribe('video:new')
    listen = types.coroutine(ps.listen)
    while not stop_app.is_set():
        msg = ps.get_message()
        if msg:
            new_video_handler(msg)
        await asyncio.sleep(0.01)

    # async for msg in generator():
    # while True:
    #     msg = await generator()


async def handler(websocket, path):
    listeners.add(websocket)
    try:
        while True:
            await websocket.recv()
    # except websockets.exceptions.ConnectionClosed:
    #     pass
    finally:
        listeners.remove(websocket)

def run():
    stop_app = asyncio.Event()

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, stop_running, loop, stop_app)
    loop.add_signal_handler(signal.SIGTERM, stop_running, loop, stop_app)

    server_config = websockets.serve(handler, 'localhost', 8765)
    ws_server = loop.run_until_complete(server_config)
    print('After run until complete', ws_server, server_config)
    loop.run_until_complete(setup_redis(loop, stop_app))

    ws_server.close()
    loop.run_until_complete(ws_server.wait_closed())
    loop.close()

def stop_running(loop, stop_app):
    print('Stopping event loop', loop)
    stop_app.set()

def start():
    proc = multiprocessing.Process(target=run)
    proc.start()

if __name__ == '__main__':
    run()
