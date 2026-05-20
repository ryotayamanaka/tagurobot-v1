import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

# J3: ch0, 270度サーボ
j3 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500, actuation_range=270)
# J2: ch6, 180度サーボ
j2 = servo.Servo(pca.channels[6], min_pulse=500, max_pulse=2500, actuation_range=180)

print("両サーボを 0度 に移動します (組み立て用)")
print("J2 (ch6, 180度) -> 0度")
j2.angle = 0
print("J3 (ch0, 270度) -> 0度")
j3.angle = 0

time.sleep(3)

print("ホーンを取り付けてください")
print("Enterで終了")
input()

pca.deinit()
print("完了")
