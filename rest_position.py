"""接続されている全脚を休眠姿勢 (足がまっすぐ伸びた状態) に移動するスクリプト。

組み立て後の動作確認や、何か実行する前の初期姿勢として使う。

  J1 (180度) -> 90度  (中央)
  J2 (180度) -> 90度  (中央)
  J3 (270度) -> 135度 (物理中央)
"""
import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

import leg_config

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50


def make_servo(channel, actuation_range):
    return servo.Servo(
        pca.channels[channel],
        min_pulse=500,
        max_pulse=2500,
        actuation_range=actuation_range,
    )


print(f"対象の脚: {[leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]}")
print("休眠姿勢 (足まっすぐ) に移動します")

# 先端 (J3) から順に動かして、機構の干渉を避ける
print("J3 -> 135度")
for group_id in leg_config.CONNECTED_LEGS:
    make_servo(leg_config.get_j3_channel(group_id), 270).angle = 135
    time.sleep(0.2)

print("J2 -> 90度")
for group_id in leg_config.CONNECTED_LEGS:
    make_servo(leg_config.get_j2_channel(group_id), 180).angle = 90
    time.sleep(0.2)

print("J1 -> 90度")
for group_id in leg_config.CONNECTED_LEGS:
    make_servo(leg_config.get_j1_channel(group_id), 180).angle = 90
    time.sleep(0.2)

input("\n休眠姿勢になりました。Enterで終了")

pca.deinit()
print("完了")
