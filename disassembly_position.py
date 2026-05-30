"""サーボを取り外しやすい姿勢 (= 組み立て時のホーン取付角度) に戻すスクリプト。

J1/J3 の入れ替え作業や、機構を分解する前に実行する。
現在のサーボ構成 (J1=270度, J2=180度, J3=180度) で動作する。
"""
import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

# J1: ch1, 270度サーボ
j1 = servo.Servo(pca.channels[1], min_pulse=500, max_pulse=2500, actuation_range=270)
# J3: ch0, 180度サーボ
j3 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500, actuation_range=180)
# J2: ch6, 180度サーボ
j2 = servo.Servo(pca.channels[6], min_pulse=500, max_pulse=2500, actuation_range=180)

print("サーボを取り外し位置に移動します")

# J3 から動かす (先端から順に戻していくと、機構の干渉が起きにくい)
print("J3 (ch0, 180度) -> 180度 (組み立て時のホーン位置)")
j3.angle = 180
time.sleep(0.5)

print("J2 (ch6, 180度) -> 0度 (組み立て時のホーン位置)")
j2.angle = 0
time.sleep(0.5)

print("J1 (ch1, 270度) -> 135度 (物理中央)")
j1.angle = 135
time.sleep(0.5)

input("\nサーボを取り外せる姿勢になりました。Enterで終了")

pca.deinit()
print("完了")
