from vehicle_control import VehicleControl
import common
import vehicle_config


class VehicleSteering:
    def __init__(self, vehicle_control: VehicleControl):
        self.vehicle_control = vehicle_control

    def start_vehicle(self):
        self.vehicle_control.start_steering()
        self.vehicle_control.start_throttle()

    def stop_vehicle(self):
        self.vehicle_control.stop_throttle()

    def turn_vehicle_right(self, turn_value: int):
        raw_pwm_cycle_duty = common.map_value(
            turn_value,
            0,
            100,
            vehicle_config.NEUTRAL_PWM_RAW,
            vehicle_config.MAX_RIGHT_PWM_RAW,
        )
        self.vehicle_control.set_pwm_duty_cycle_for_steering(
            raw_pwm_cycle_duty)

    def turn_vehicle_left(self, turn_value: int):
        raw_pwm_cycle_duty = common.map_value(
            turn_value,
            0,
            100,
            vehicle_config.NEUTRAL_PWM_RAW,
            vehicle_config.MAX_LEFT_PWM_RAW,
        )
        self.vehicle_control.set_pwm_duty_cycle_for_steering(
            raw_pwm_cycle_duty)

    def center_steering(self):
        self.vehicle_control.set_pwm_duty_cycle_for_steering(
            vehicle_config.NEUTRAL_PWM_RAW)

    def drive_forward(self, speed_value: int):
        raw_pwm_cycle_duty = common.map_value(
            speed_value,
            0,
            100,
            vehicle_config.PWM_MIN_RAW_VALUE,
            vehicle_config.PWM_MAX_RAW_VALUE,
        )
        self.vehicle_control.set_throttle_direction_forward()
        self.vehicle_control.set_pwm_duty_cycle_for_motors(raw_pwm_cycle_duty)

    def set_speed_for_right_motor(self, speed_value: int):
        raw_pwm_cycle_duty = common.map_value(
            speed_value,
            0,
            100,
            vehicle_config.PWM_MIN_RAW_VALUE,
            vehicle_config.PWM_MAX_RAW_VALUE,
        )
        self.vehicle_control.set_throttle_direction_forward()
        self.vehicle_control.set_pwm_duty_cycle_for_right_motor(
            raw_pwm_cycle_duty)

    def set_speed_for_left_motor(self, speed_value: int):
        raw_pwm_cycle_duty = common.map_value(
            speed_value,
            0,
            100,
            vehicle_config.PWM_MIN_RAW_VALUE,
            vehicle_config.PWM_MAX_RAW_VALUE,
        )
        self.vehicle_control.set_throttle_direction_forward()
        self.vehicle_control.set_pwm_duty_cycle_for_left_motor(
            raw_pwm_cycle_duty)

    def drive_backward(self, speed_value: int):
        raw_pwm_cycle_duty = common.map_value(
            speed_value,
            0,
            100,
            vehicle_config.PWM_MIN_RAW_VALUE,
            vehicle_config.PWM_MAX_RAW_VALUE,
        )
        self.vehicle_control.set_throttle_direction_backward()
        self.vehicle_control.set_pwm_duty_cycle_for_motors(raw_pwm_cycle_duty)
