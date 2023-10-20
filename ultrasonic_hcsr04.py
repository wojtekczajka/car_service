import RPi.GPIO as GPIO
import time
import threading

class DistanceSensor:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.PIN_TRIGGER = 4
        self.PIN_ECHO = 17
        GPIO.setup(self.PIN_TRIGGER, GPIO.OUT)
        time.sleep(0.1)
        GPIO.setup(self.PIN_ECHO, GPIO.IN)
        time.sleep(0.1)
        GPIO.output(self.PIN_TRIGGER, GPIO.LOW)
        time.sleep(0.1)
        self.distance = 0.0
        self.lock = threading.Lock()
        self.update_frequency = 5  # Updates n times per second
        self.update_thread = threading.Thread(target=self._update_distance)
        self.update_thread.daemon = True
        self.update_thread.start()

    def _update_distance(self):
        while True:
            distance = self._measure_distance()
            with self.lock:
                self.distance = distance
            time.sleep(1 / self.update_frequency)

    def _measure_distance(self):
        GPIO.output(self.PIN_TRIGGER, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.PIN_TRIGGER, GPIO.LOW)

        while GPIO.input(self.PIN_ECHO) == 0:
            pulse_start_time = time.time()
        while GPIO.input(self.PIN_ECHO) == 1:
            pulse_end_time = time.time()

        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(pulse_duration * 17150, 2)
        return distance

    def measure_distance(self):
        with self.lock:
            return self.distance

    def cleanup(self):
        GPIO.cleanup()

    def __del__(self):
        self.cleanup()

# Usage:
# sensor = DistanceSensor()
# while True:
#     distance = sensor.measure_distance()
#     print(f"Distance: {distance} cm")
#     time.sleep(1)
