import asyncio
import websockets
import multiprocessing
import json
from motionweb import utils

listeners = set()

class EchoServerClientProtocol(asyncio.Protocol):
    def data_received(self, data):
        filename = data.decode().strip()
        video = utils.video_to_dict(filename)
        obj = json.dumps(video)
        print('Data received: {}'.format(filename))
        print("Listeners: {}".format(listeners))
        for l in listeners:
            asyncio.ensure_future(l.send(obj))
        print('Sent: {}'.format(video))

    def eof_received(self):
        print('EOF Received')

async def handler(websocket, path):
    listeners.add(websocket)
    try:
        while True:
            # await websocket.ping()
            await asyncio.sleep(10)
    # except websockets.exceptions.ConnectionClosed:
    #     pass
    finally:
        listeners.remove(websocket)

def run():
    loop = asyncio.get_event_loop()
    ws_server = websockets.serve(handler, 'localhost', 8765)
    skt_server = loop.create_server(EchoServerClientProtocol, 'localhost', 8888)
    loop.run_until_complete(ws_server)
    loop.run_until_complete(skt_server)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

def start():
    proc = multiprocessing.Process(target=run)
    proc.start()

if __name__ == '__main__':
    run()
