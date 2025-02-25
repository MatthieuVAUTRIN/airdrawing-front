import asyncio
import os
from queue import Queue
from threading import Thread

import cv2
import numpy as np
import websockets

WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "ws://localhost:8000/ws")


class WebSocketClient:
    def __init__(self):
        self.frame_queue = Queue()
        self.result_queue = Queue()
        self.draw_color = (0, 255, 0)
        self.running = True

    async def connect_websocket(self):
        while self.running:
            try:
                async with websockets.connect(WEBSOCKET_URL) as websocket:
                    while self.running:
                        if not self.frame_queue.empty():
                            frame = self.frame_queue.get()

                            # encode frame to jpg for lower resolution
                            _, buffer = cv2.imencode(
                                ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50]
                            )

                            await websocket.send(buffer.tobytes())

                            response_img = await websocket.recv()
                            img_array = np.frombuffer(response_img, np.uint8)
                            processed_frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                            self.result_queue.put(processed_frame)

                        await asyncio.sleep(0.0001)
            except websockets.exceptions.ConnectionClosed:
                await asyncio.sleep(1)  # sleep for a while before reconnecting
            except Exception as e:
                print(f"WebSocket error: {str(e)}")
                await asyncio.sleep(1)

    def run_websocket(self):
        asyncio.run(self.connect_websocket())

    def start(self):
        self.thread = Thread(target=self.run_websocket, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
