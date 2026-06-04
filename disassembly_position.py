"""接続されている全脚のサーボを取り外し/取り付け位置に移動するスクリプト。

機構の分解、サーボの追加、ホーンの取り付けなどに使う。
組み立て時のホーン取付角度と同じ位置に動かす。

  J1 (180度) -> 90度  (物理中央)
  J2 (180度) -> 0度   (組み立て位置)
  J3 (270度) -> 225度 (組み立て位置)
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

# 先端 (J3) から順に動かすと機構の干渉が起きにくい
print("J3 (270度) -> 225度 (オフセット適用済み)")
for group_id in leg_config.CONNECTED_LEGS:
    ch = leg_config.get_j3_channel(group_id)
    angle = leg_config.apply_offset(225, group_id, "j3")
    print(f"  脚{leg_config.leg_name(group_id)} (ch{ch}) -> {angle}度")
    make_servo(ch, 270).angle = angle
    time.sleep(0.3)

print("J2 (180度) -> 0度 (オフセット適用済み)")
for group_id in leg_config.CONNECTED_LEGS:
    ch = leg_config.get_j2_channel(group_id)
    angle = leg_config.apply_offset(0, group_id, "j2")
    print(f"  脚{leg_config.leg_name(group_id)} (ch{ch}) -> {angle}度")
    make_servo(ch, 180).angle = angle
    time.sleep(0.3)

print("J1 (180度) -> 90度 (オフセット適用済み)")
for group_id in leg_config.CONNECTED_LEGS:
    ch = leg_config.get_j1_channel(group_id)
    angle = leg_config.apply_offset(90, group_id, "j1")
    print(f"  脚{leg_config.leg_name(group_id)} (ch{ch}) -> {angle}度")
    make_servo(ch, 180).angle = angle
    time.sleep(0.3)

input("\n取り外し可能な姿勢になりました。Enterで終了 (サーボの保持トルクが切れる)")

pca.deinit()
print("完了")
