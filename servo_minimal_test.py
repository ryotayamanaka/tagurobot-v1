import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

# PCA9685の初期化
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

# ch0に180度サーボを設定
my_servo = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500, actuation_range=180)

print("サーボテスト開始")

print("90度（中央）に移動")
my_servo.angle = 90
time.sleep(2)

print("0度に移動")
my_servo.angle = 0
time.sleep(2)

print("180度に移動")
my_servo.angle = 180
time.sleep(2)

print("90度（中央）に戻す")
my_servo.angle = 90
time.sleep(2)

pca.deinit()
print("テスト完了")
