import busio

from board import SCL, SDA
from adafruit_pca9685 import PCA9685

import vehicle_config


class VehicleControl:
    def __init__(self, i2c_bus: busio.I2C, steering_pwm_controller: PCA9685, throttle_pwm_controller: PCA9685):
        self.i2c_bus = i2c_bus
        self.steering_pwm_controller = steering_pwm_controller
        self.throttle_pwm_controller = throttle_pwm_controller
        self.steering_pwm_controller.frequency = vehicle_config.PWM_FREQ_50HZ
        self.throttle_pwm_controller.frequency = vehicle_config.PWM_FREQ_50HZ

    def stop_throttle(self):
        self.set_pwm_duty_cycle_for_motors(vehicle_config.PWM_MIN_RAW_VALUE)

    def set_pwm_duty_cycle_on_controller_channel(self, controller, channel, pwm_duty_cycle):
        controller.channels[channel].duty_cycle = pwm_duty_cycle

    def start_steering(self):
        self.set_pwm_duty_cycle_on_controller_channel(
            self.steering_pwm_controller,
            vehicle_config.PWM_STEERING_CHANNEL,
            vehicle_config.NEUTRAL_PWM_RAW,
        )

    def start_throttle(self):
        self.set_throttle_direction_forward()
        self.set_pwm_duty_cycle_for_motors(vehicle_config.PWM_MIN_RAW_VALUE)

    def set_throttle_direction_forward(self):
        self.set_pwm_duty_cycle_on_controller_channel(
            self.throttle_pwm_controller,
            vehicle_config.PWM_THROTTLE_CHANNEL_LEFT_MOTOR_IN1,
            vehicle_config.PWM_MAX_RAW_VALUE,
        )
        self.set_pwm_duty_cycle_on_controller_channel(
            self.throttle_pwm_controller,
            vehicle_config.PWM_THROTTLE_CHANNEL_LEFT_MOTOR_IN2,
            vehicle_config.PWM_MIN_RAW_VALUE,
        )
        self.set_pwm_duty_cycle_on_controller_channel(
            self.throttle_pwm_controller,
            vehicle_config.PWM_THROTTLE_CHANNEL_RIGHT_MOTOR_IN1,
            vehicle_config.PWM_MIN_RAW_VALUE,
        )
        self.set_pwm_duty_cycle_on_controller_channel(
            self.throttle_pwm_controller,
            vehicle_config.PWM_THROTTLE_CHANNEL_RIGHT_MOTOR_IN2,
            vehicle_config.PWM_MAX_RAW_VALUE,
        )

    def set_throttle_direction_backward(self):
        self.set_pwm_duty_cycle_on_controller_channel(
            self.throttle_pwm_controller,
            vehicle_config.PWM_THROTTLE_CHANNEL_LEFT_MOTOR_IN1,
            vehicle_config.PWM_MIN_RAW_VALUE,
        )
        self.set_pwm_duty_cycle_on_controller_channel(
            self.throttle_pwm_controller,
            vehicle_config.PWM_THROTTLE_CHANNEL_LEFT_MOTOR_IN2,
            vehicle_config.PWM_MAX_RAW_VALUE,
        )
        self.set_pwm_duty_cycle_on_controller_channel(
            self.throttle_pwm_controller,
            vehicle_config.PWM_THROTTLE_CHANNEL_RIGHT_MOTOR_IN1,
            vehicle_config.PWM_MAX_RAW_VALUE,
        )
        self.set_pwm_duty_cycle_on_controller_channel(
            self.throttle_pwm_controller,
            vehicle_config.PWM_THROTTLE_CHANNEL_RIGHT_MOTOR_IN2,
            vehicle_config.PWM_MIN_RAW_VALUE,
        )

    def set_pwm_duty_cycle_for_steering(self, pwm_duty_cycle: int):
        self.validate_pwm_cycle_duty_for_steering(pwm_duty_cycle)
        self.set_pwm_duty_cycle_on_controller_channel(
            self.steering_pwm_controller,
            vehicle_config.PWM_STEERING_CHANNEL,
            pwm_duty_cycle,
        )

    def validate_pwm_cycle_duty_for_steering(self, pwm_cycle_duty: int):
        if not (
            vehicle_config.MAX_LEFT_PWM_RAW
            <= pwm_cycle_duty
            <= vehicle_config.MAX_RIGHT_PWM_RAW
        ):
            raise ValueError(
                f"PWM RAW CYCLE DUTY value for steering should be between "
                f"{vehicle_config.MAX_LEFT_PWM_RAW} and {vehicle_config.MAX_RIGHT_PWM_RAW}."
            )

    def set_pwm_duty_cycle_for_motors(self, pwm_duty_cycle: int):
        self.validate_pwm_cycle_duty_for_motors(pwm_duty_cycle)
        self.set_pwm_duty_cycle_on_controller_channel(
            self.throttle_pwm_controller,
            vehicle_config.PWM_THROTTLE_CHANNEL_LEFT_MOTOR_PWM,
            pwm_duty_cycle,
        )
        self.set_pwm_duty_cycle_on_controller_channel(
            self.throttle_pwm_controller,
            vehicle_config.PWM_THROTTLE_CHANNEL_RIGHT_MOTOR_PWM,
            pwm_duty_cycle,
        )

    def set_pwm_duty_cycle_for_left_motor(self, pwm_duty_cycle: int):
        self.set_throttle_direction_forward()
        self.validate_pwm_cycle_duty_for_motors(pwm_duty_cycle)
        self.set_pwm_duty_cycle_on_controller_channel(
            self.throttle_pwm_controller,
            vehicle_config.PWM_THROTTLE_CHANNEL_LEFT_MOTOR_PWM,
            pwm_duty_cycle,
        )

    def set_pwm_duty_cycle_for_right_motor(self, pwm_duty_cycle: int):
        self.set_throttle_direction_forward()
        self.validate_pwm_cycle_duty_for_motors(pwm_duty_cycle)
        self.set_pwm_duty_cycle_on_controller_channel(
            self.throttle_pwm_controller,
            vehicle_config.PWM_THROTTLE_CHANNEL_RIGHT_MOTOR_PWM,
            pwm_duty_cycle,
        )

    def validate_pwm_cycle_duty_for_motors(self, pwm_cycle_duty: int):
        if not (
            vehicle_config.PWM_MIN_RAW_VALUE
            <= pwm_cycle_duty
            <= vehicle_config.PWM_MAX_RAW_VALUE
        ):
            raise ValueError(
                f"PWM RAW CYCLE DUTY value for motors should be between "
                f"{vehicle_config.PWM_MIN_RAW_VALUE} and {vehicle_config.PWM_MAX_RAW_VALUE}."
            )
