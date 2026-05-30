"""サーボを取り外しやすい姿勢 (= 組み立て時のホーン取付角度) に移動するスクリプト。

機構を分解したり、サーボを脚や胴体から取り外す前に実行する。
組み立てる時にホーンを取り付ける姿勢と同じなので、ホーンを動かさずに
サーボ本体を機構から外せる。

サーボ構成:
  J1 (ch12, 180度) -> 90度 (物理中央)
  J2 (ch6,  180度) -> 0度  (組み立て位置)
  J3 (ch0,  270度) -> 135度 (物理中央)
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

print("サーボを取り外し位置に移動します")

# 先端 (J3) から順に動かすと機構の干渉が起きにくい
print("J3 (ch0, 270度) -> 135度 (物理中央)")
j3.angle = 135
time.sleep(0.5)

print("J2 (ch6, 180度) -> 0度 (組み立て位置)")
j2.angle = 0
time.sleep(0.5)

print("J1 (ch12, 180度) -> 90度 (物理中央)")
j1.angle = 90
time.sleep(0.5)

input("\n取り外し可能な姿勢になりました。Enterで終了 (サーボの保持トルクが切れる)")

pca.deinit()
print("完了")
