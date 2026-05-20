import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

# J3: ch0, 180度サーボ, 中立角度 90度 (物理中央)
j3 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500, actuation_range=180)
# J2: ch6, 180度サーボ, 中立角度 140度
j2 = servo.Servo(pca.channels[6], min_pulse=500, max_pulse=2500, actuation_range=180)

print("両サーボを中立角度に移動します (組み立て姿勢)")
print("J2 (ch6, 180度) -> 0度")
j2.angle = 0
print("J3 (ch0, 180度) -> 180度")
j3.angle = 180

time.sleep(3)

print("ホーンの向きを確認してください")
print("Enterで終了")
input()

pca.deinit()
print("完了")
