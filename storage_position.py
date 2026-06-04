"""接続されている全脚を収納姿勢に折りたたむスクリプト。

しまう時にコンパクトな姿勢にする。

  J1 (180度) -> 90度  (中央)
  J2 (180度) -> 170度  (上限180度に余裕を持たせた値、オフセットで超えないように)
  J3 (270度) -> 40度
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
print("収納姿勢に折りたたみます")

# まず J1 を中央に戻して脚の向きを揃える
print("J1 (180度) -> 90度 (中央, オフセット適用済み)")
for group_id in leg_config.CONNECTED_LEGS:
    angle = leg_config.apply_offset(90, group_id, "j1")
    make_servo(leg_config.get_j1_channel(group_id), 180).angle = angle
    time.sleep(0.3)

# 次に J2 を 170度に (180度サーボの上限180度から余裕を持たせる)
print("J2 (180度) -> 170度 (オフセット適用済み)")
for group_id in leg_config.CONNECTED_LEGS:
    angle = leg_config.apply_offset(170, group_id, "j2")
    make_servo(leg_config.get_j2_channel(group_id), 180).angle = angle
    time.sleep(0.3)

# 最後に J3 を 40度に (大きく回転するので最後)
print("J3 (270度) -> 40度 (オフセット適用済み)")
for group_id in leg_config.CONNECTED_LEGS:
    angle = leg_config.apply_offset(40, group_id, "j3")
    make_servo(leg_config.get_j3_channel(group_id), 270).angle = angle
    time.sleep(0.3)

input("\n収納姿勢になりました。Enterで終了 (サーボの保持トルクが切れる)")

pca.deinit()
print("完了")
