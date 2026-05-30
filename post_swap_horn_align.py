"""J1/J3 入れ替え後、各サーボを既存ホーンの取付位置に合わせるスクリプト。

入れ替え後のサーボ構成 (J1=180度, J2=180度, J3=270度) で動作する。
ホーンは入れ替え前の位置のままなので、サーボを動かしてホーンに合わせる。

- J1 (180度): 既存ホーンは元 270度サーボで 135度位置にあった。
  暫定的に 180度サーボでも 135度を指示してホーンの向きを目視確認する。
- J2 (180度): 変更なし。0度のまま。
- J3 (270度): 既存ホーンは元 180度サーボで 180度位置にあった。
  270度サーボでも 180度を指示すれば物理的に同じ位置になる想定。
"""
import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

# 入れ替え後の構成
j1 = servo.Servo(pca.channels[1], min_pulse=500, max_pulse=2500, actuation_range=180)
j2 = servo.Servo(pca.channels[6], min_pulse=500, max_pulse=2500, actuation_range=180)
j3 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500, actuation_range=270)

print("入れ替え後のサーボ構成でホーン位置に合わせます")

print("J3 (ch0, 270度) -> 180度")
j3.angle = 180
time.sleep(0.5)

print("J2 (ch6, 180度) -> 0度")
j2.angle = 0
time.sleep(0.5)

print("J1 (ch1, 180度) -> 135度 (暫定)")
j1.angle = 135
time.sleep(0.5)

print("\nホーンの向きを確認してください")
print("問題なければサーボを取り付けて Enter で終了")
input()

pca.deinit()
print("完了")
