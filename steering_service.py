from adafruit_pca9685 import PCA9685
from board import SCL, SDA
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import busio

from ultrasonic_hcsr04 import DistanceSensor
from vehicle_control import VehicleControl
from vehicle_steering import VehicleSteering

import vehicle_config


class Action(BaseModel):
    action: str
    value: int = None


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

distance_sensor = DistanceSensor()


@app.get("/distance")
async def get_distance():
    return {"distance": distance_sensor.measure_distance()}


@app.post("/control")
async def control_vehicle(action_data: Action):
    action = action_data.action
    value = action_data.value

    if value is not None and not (0 <= value <= 100):
        raise HTTPException(
            status_code=404, detail="Value must be in the range 0 to 100")

    action_handler, args = action_handlers.get(action, (None, ()))

    if action_handler is not None:
        if "value" in args:
            action_handler(value)
        else:
            action_handler()
        return ("Action performed successfully")
    else:
        raise HTTPException(
            status_code=404, detail="Invalid action or missing value")
