"""脚を収納姿勢に折りたたむスクリプト。

しまう時にコンパクトな姿勢にする。

  J1 (ch12, 180度) -> 90度  (中央)
  J2 (ch6,  180度) -> 180度
  J3 (ch0,  270度) -> 40度
"""
import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

j1 = servo.Servo(pca.channels[12], min_pulse=500, max_pulse=2500, actuation_range=180)
j2 = servo.Servo(pca.channels[6], min_pulse=500, max_pulse=2500, actuation_range=180)
j3 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500, actuation_range=270)

print("収納姿勢に折りたたみます")

# 先に J1 を中央に戻して脚の向きを揃える
print("J1 (ch12, 180度) -> 90度 (中央)")
j1.angle = 90
time.sleep(0.5)

# 次に J2 を 180度に
print("J2 (ch6, 180度) -> 180度")
j2.angle = 180
time.sleep(0.5)

# 最後に J3 を 40度に (大きく回転するので最後)
print("J3 (ch0, 270度) -> 40度")
j3.angle = 40
time.sleep(0.5)

input("\n収納姿勢になりました。Enterで終了 (サーボの保持トルクが切れる)")

pca.deinit()
print("完了")
