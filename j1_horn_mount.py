"""J1サーボ (ch12, 180度) を中立角度 90度に固定してホーン取り付けを行うスクリプト。

ホーン取り付けが完了したら Enter で終了する。
"""
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

CHANNEL = 12

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

j1 = servo.Servo(
    pca.channels[CHANNEL],
    min_pulse=500,
    max_pulse=2500,
    actuation_range=180,
)

print(f"J1 (ch{CHANNEL}, 180度) を 90度 (物理中央) に移動します")
j1.angle = 90

input("ホーンを取り付けたら Enter で終了")

pca.deinit()
print("完了")
