from adafruit_pca9685 import PCA9685
from board import SCL, SDA
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import busio

from ultrasonic_hcsr04 import DistanceSensor
from vehicle_control import VehicleControl
from vehicle_steering import VehicleSteering

import vehicle_config

from collections import defaultdict

app = FastAPI()

i2c_bus = busio.I2C(SCL, SDA)
steering = VehicleSteering(VehicleControl(i2c_bus=i2c_bus,
                                          steering_pwm_controller=PCA9685(
                                              i2c_bus, address=vehicle_config.I2C_STEERING_PWM_CONTROLLER_ADDRESS),
                                          throttle_pwm_controller=PCA9685(i2c_bus, address=vehicle_config.I2C_THROTTLE_PWM_CONTROLLER_ADDRESS)))
steering.center_steering()
action_handlers = {
    "start": (steering.start_vehicle, ()),
    "stop": (steering.stop_vehicle, ()),
    "center": (steering.center_steering, ()),
    "turn_left": (steering.turn_vehicle_left, ("value",)),
    "turn_right": (steering.turn_vehicle_right, ("value",)),
    "drive_forward": (steering.drive_forward, ("value",)),
    "drive_backward": (steering.drive_backward, ("value",)),
    "set_speed_for_right_motor": (steering.set_speed_for_right_motor, ("value",)),
    "set_speed_for_left_motor": (steering.set_speed_for_left_motor, ("value",)),
}


class FrameStorage:
    def __init__(self):
        self.frame_data = None
        self.frame_updated = False


video_frames = defaultdict(FrameStorage)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Video Streams</title>
    </head>
    <body>
        <h1>Video Streams</h1>
        %s
    </body>
</html>
""" % "\n".join([f'<img id="video_{name}" width="640" height="368" src="/video_feed?name={name}"/>' for name in video_frames.keys()])

distance_sensor = DistanceSensor()


class Action(BaseModel):
    action: str
    value: int = None


class Frame(BaseModel):
    frame_title: str
    frame_data: str


def gen_frames(frame_name: str):
    while True:
        if video_frames[frame_name].frame_updated:
            video_frames[frame_name].frame_updated = False
            yield (b'--frame\r\n'
                   b'Content-Type: image/base64\r\n\r\n' + video_frames[frame_name].frame_data + b'\r\n')


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
async def video_feed(name: str):
    if name not in video_frames:
        return "Video not found"

    return StreamingResponse(gen_frames(name), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/distance")
async def get_distance():
    return {"distance": distance_sensor.measure_distance()}


@app.post("/control")
async def control_vehicle(action_data: Action):
    action = action_data.action
    value = action_data.value

    if value is not None and not (0 <= value <= 100):
        raise HTTPException(status_code=404, detail="Value must be in the range 0 to 100")
    
    action_handler, args = action_handlers.get(action, (None, ()))

    if action_handler is not None:
        if "value" in args:
            action_handler(value)
        else:
            action_handler()
        return("Action performed successfully")
    else:
        raise HTTPException(status_code=404, detail="Invalid action or missing value")


@app.post("/frame_dispatcher")
async def dispatch_frame(frame: Frame):
    global html
    video_frames[frame.frame_title].frame_data = frame.frame_data
    video_frames[frame.frame_title].frame_updated = True

    if f'id="video_{frame.frame_title}"' not in html:
                    new_video_element = f'<div><h2>{frame.frame_title}</h2><img id="video_{frame.frame_title}" width="640" height="368" src="/video_feed?name={frame.frame_title}"/></div>'
                    html = html.replace(
                        '</body>', f'{new_video_element}</body>')
    return {"detail": "ok"}
