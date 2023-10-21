from adafruit_pca9685 import PCA9685
from board import SCL, SDA
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from threading import Lock

import busio
import json

from ultrasonic_hcsr04 import DistanceSensor
from vehicle_control import VehicleControl
from vehicle_steering import VehicleSteering

import vehicle_config

app = FastAPI()

i2c_bus = busio.I2C(SCL, SDA)
steering = VehicleSteering(VehicleControl(i2c_bus=i2c_bus,
                                          steering_pwm_controller=PCA9685(
                                              i2c_bus, address=vehicle_config.I2C_STEERING_PWM_CONTROLLER_ADDRESS),
                                          throttle_pwm_controller=PCA9685(i2c_bus, address=vehicle_config.I2C_THROTTLE_PWM_CONTROLLER_ADDRESS)))

action_handlers = {
    "start": (steering.start_vehicle, ()),
    "stop": (steering.stop_vehicle, ()),
    "turn_left": (steering.turn_vehicle_left, ("value",)),
    "turn_right": (steering.turn_vehicle_right, ("value",)),
    "center": (steering.center_steering, ()),
    "drive_forward": (steering.drive_forward, ("value",)),
    "drive_backward": (steering.drive_backward, ("value",)),
    "set_speed_for_right_motor": (steering.set_speed_for_right_motor, ("value",)),
    "set_speed_for_left_motor": (steering.set_speed_for_left_motor, ("value",)),
}

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Video Stream</title>
    </head>
    <body>
        <h1>Video Stream</h1>
        <img id="video" width="640" height="368" src="http://127.0.0.1:8000/video_feed"/>
    </body>
</html>
"""

distance_sensor = DistanceSensor()


class Action(BaseModel):
    action: str
    value: int = None


class FrameStorage:
    def __init__(self):
        self.frame_data = None
        self.frame_updated = False
        self.lock = Lock()


frame_storage = FrameStorage()


def gen_frames():
    while True:
        if frame_storage.frame_updated:
            with frame_storage.lock:
                frame_storage.frame_updated = False
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_storage.frame_data + b'\r\n')


async def perform_action(websocket, action_data):
    action = action_data.get("action")
    value = action_data.get("value")

    if value is not None and not (0 <= value <= 100):
        await websocket.send_text("Value must be in the range 0 to 100")
        return

    action_handler, args = action_handlers.get(action, (None, ()))

    if action_handler is not None:
        if "value" in args:
            action_handler(value)
        else:
            action_handler()
        await websocket.send_text("Action performed successfully")
    else:
        await websocket.send_text("Invalid action or missing value")


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.websocket("/distance")
async def get_distance(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
            distance = distance_sensor.measure_distance()
            await websocket.send_text(str(distance))
    except WebSocketDisconnect:
        pass


@app.websocket("/control")
async def control_vehicle(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            action_data = json.loads(data)
            await perform_action(websocket=websocket, action_data=action_data)
    except WebSocketDisconnect:
        pass


@app.websocket("/frame_dispatcher")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            frame_data = await websocket.receive_bytes()
            await websocket.send_text("data received")
            if frame_data:
                with frame_storage.lock:
                    frame_storage.frame_data = frame_data
                    frame_storage.frame_updated = True
    except WebSocketDisconnect:
        pass
