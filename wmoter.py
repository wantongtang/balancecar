from mpu6050 import mpu6050
from time import sleep
import math
import  RPi.GPIO as GPIO
import time
from PID import PID
from pidcontroller import PIDController


motora_in1 = 21
motora_in2 = 20
motora_pwm = 16

motorb_in1 = 13
motorb_in2 = 19
motorb_pwm = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(motora_in1, GPIO.OUT)
GPIO.setup(motora_in2, GPIO.OUT)
GPIO.setup(motora_pwm, GPIO.OUT)
GPIO.setup(motorb_in1, GPIO.OUT)
GPIO.setup(motorb_in2, GPIO.OUT)
GPIO.setup(motorb_pwm, GPIO.OUT)

pwm_a = GPIO.PWM(motora_pwm, 100)
pwm_b = GPIO.PWM(motorb_pwm, 100)
pwm_a.start(0)
pwm_b.start(0)

def forward(velocity):
	GPIO.output(motora_in1, GPIO.HIGH)
	GPIO.output(motora_in2, GPIO.LOW)
	pwm_a.ChangeDutyCycle(velocity)
	
	GPIO.output(motorb_in1, GPIO.HIGH)
	GPIO.output(motorb_in2, GPIO.LOW)
	pwm_b.ChangeDutyCycle(velocity)
	
def backward(velocity):
	GPIO.output(motora_in1, GPIO.LOW)
	GPIO.output(motora_in2, GPIO.HIGH)
	pwm_a.ChangeDutyCycle(velocity)
	
	GPIO.output(motorb_in1, GPIO.LOW)
	GPIO.output(motorb_in2, GPIO.HIGH)
	pwm_b.ChangeDutyCycle(velocity)

def stand_still():
	GPIO.output(motora_in1, GPIO.LOW)
	GPIO.output(motora_in2, GPIO.LOW)
	GPIO.output(motorb_in1, GPIO.LOW)
	GPIO.output(motorb_in2, GPIO.LOW)


def distance(a,b):
	return math.sqrt((a*a)+(b*b))
def y_rotation(x,y,z):
	radians = math.atan2(x, distance(y, z))
	return -math.degrees(radians)
def x_rotation(x,y,z):
	radians = math.atan2(y, distance(x, z))
	return math.degrees(radians)


sensor = mpu6050(0x68)
accel_data = sensor.get_accel_data()
gyro_data = sensor.get_gyro_data()
aTempX = accel_data['x']
aTempY = accel_data['y']
aTempZ = accel_data['z']

gTempX = gyro_data['x']
gTempY = gyro_data['y']
gTempZ = gyro_data['z']
last_x = x_rotation(aTempX, aTempY, aTempZ)
last_y = y_rotation(aTempX, aTempY, aTempZ)
gyro_offset_x = gTempX
gyro_offset_y = gTempY
gx_total = (last_x) - gyro_offset_x
gy_total = (last_y) - gyro_offset_y


time_diff = 0.04
K = 0.98

PID1 = PIDController(P=-35, I=-1.5, D=-0.1)
PID1.setTarget(7.5)
while True:
	try:
#		forward(30)
#		time.sleep(2)
#		backward(30)
#		time.sleep(2)
#		stand_still()
#		time.sleep(2)
		accel_data = sensor.get_accel_data()
		gyro_data = sensor.get_gyro_data()
		
		ax = accel_data['x']
		ay = accel_data['y']
		az = accel_data['z']
		
		gx = gyro_data['x']
		gy = gyro_data['y']
		gy = gyro_data['z']
		
		gx -= gyro_offset_x
		gy -= gyro_offset_y
		
		gx_delta = (gx *time_diff)
		gy_delta = (gy *time_diff)
		gx_total += gx_delta
		gy_total += gy_delta
		
		rot_x = x_rotation(ax,ay,az)
		rot_y = y_rotation(ax,ay,az)

		# complementary Filter
		last_x = K *(last_x + gx_delta) + (1-K)*rot_x
		
#		print(last_x)
		PIDx = PID1.step(last_x)
		pid1 = PIDx
		print pid1		
		
		if pid1 > 100:
			pid1 = 100
		if pid1 < -100:
			pid1 = -100
		if pid1 < 0.0:
			backward(-(pid1))
		elif pid1 >0.0:
			forward(pid1)
		else:
			stand_still()
								


		time.sleep(0.04)
	except KeyboardInterrupt:
		pwm_a.stop()
		pwm_b.stop()
		GPIO.cleanup()
		exit()
	
