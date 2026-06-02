"""休眠姿勢から J2/J3 を少しずつ動かして胴体を持ち上げる動作テスト。

3脚で胴体の自重を支えられるかを検証する。
段階的に角度を上げていくので、途中で異常があれば Ctrl+C で止める。

  休眠姿勢: J2=90度, J3=135度 (足まっすぐ)
  立ち上がり: J2=90度+OFFSET, J3=135度+OFFSET (足を少し曲げて持ち上げ)
"""
import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

import leg_config

# 動作パラメータ
J2_NEUTRAL = 90
J3_NEUTRAL = 135
LIFT_DEGREES = 40   # 持ち上げ量 (度)
STEP_DEGREES = 1    # 1段階あたりの角度
STEP_DELAY = 0.2    # 各段階の待機時間 (秒)

# どちら方向に動かすか (+ or -)
# 機構の取り付け方向に合わせて調整する
J2_DIR = -1
J3_DIR = +1

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


# 各脚の J2/J3 サーボを準備
legs_j2 = {}
legs_j3 = {}
for group_id in leg_config.CONNECTED_LEGS:
    legs_j2[group_id] = make_servo(leg_config.get_j2_channel(group_id), 180)
    legs_j3[group_id] = make_servo(leg_config.get_j3_channel(group_id), 270)


def set_all(j2_angle, j3_angle):
    """全脚の J2 と J3 を同時に同じ角度に設定"""
    for group_id in leg_config.CONNECTED_LEGS:
        legs_j2[group_id].angle = j2_angle
        legs_j3[group_id].angle = j3_angle


legs_str = [leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]
print(f"対象の脚: {legs_str}")
print(f"休眠姿勢 (J2={J2_NEUTRAL}度, J3={J3_NEUTRAL}度) から開始")

# まず休眠姿勢に
set_all(J2_NEUTRAL, J3_NEUTRAL)
time.sleep(1)

print(f"J2 と J3 を {LIFT_DEGREES}度ずつ動かして持ち上げます")
print("途中で異常があれば Ctrl+C で中断")

try:
    # 段階的に持ち上げ
    for offset in range(STEP_DEGREES, LIFT_DEGREES + 1, STEP_DEGREES):
        j2 = J2_NEUTRAL + J2_DIR * offset
        j3 = J3_NEUTRAL + J3_DIR * offset
        print(f"  J2={j2}度, J3={j3}度")
        set_all(j2, j3)
        time.sleep(STEP_DELAY)

    print("\n持ち上げ完了。3秒間維持します")
    time.sleep(3)

    # 段階的に戻す
    print("休眠姿勢に戻します")
    for offset in range(LIFT_DEGREES - STEP_DEGREES, -1, -STEP_DEGREES):
        j2 = J2_NEUTRAL + J2_DIR * offset
        j3 = J3_NEUTRAL + J3_DIR * offset
        print(f"  J2={j2}度, J3={j3}度")
        set_all(j2, j3)
        time.sleep(STEP_DELAY)

except KeyboardInterrupt:
    print("\n中断 - 休眠姿勢に戻します")
    set_all(J2_NEUTRAL, J3_NEUTRAL)

pca.deinit()
print("完了")
