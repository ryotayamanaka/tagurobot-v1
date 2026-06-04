"""立ち上がってから全脚の J1 を同方向に動かして胴体を回転させるスクリプト。

立った状態 (J2/J3 で持ち上げた状態) で全脚の J1 を同時に同じ方向に動かすと、
足先は地面に固定されたまま胴体が J1 の動きと逆方向に回転する。
歩行動作の前段階として、その場回転を検証する。

シーケンス:
  1. 休眠姿勢 (J1=90, J2=90, J3=135)
  2. 立ち上がる (J2 と J3 を 45 度動かして持ち上げ)
  3. 胴体を左に回転 (全脚 J1 を +25 度に)
  4. 一旦中央に戻す
  5. 胴体を右に回転 (全脚 J1 を -25 度に)
  6. 中央に戻す
  7. 着地 (J2/J3 を休眠姿勢に)
"""
import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

import leg_config

# 中立角度 (休眠姿勢)
J1_NEUTRAL = 90
J2_NEUTRAL = 90
J3_NEUTRAL = 135

# 立ち上がり量 (J2 を曲げ、J3 を伸ばす)
LIFT_DEGREES = 45
J2_DIR = -1
J3_DIR = +1

# 回転量 (J1 の中立からのオフセット、安全マージン込み)
ROTATE_DEGREES = 25

# 動作の細かさ
STEP_DEGREES = 1
STEP_DELAY = 0.15
HOLD_TIME = 1.5  # 各姿勢で維持する時間 (秒)

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


# 各脚のサーボを準備
legs_j1 = {}
legs_j2 = {}
legs_j3 = {}
for group_id in leg_config.CONNECTED_LEGS:
    legs_j1[group_id] = make_servo(leg_config.get_j1_channel(group_id), 180)
    legs_j2[group_id] = make_servo(leg_config.get_j2_channel(group_id), 180)
    legs_j3[group_id] = make_servo(leg_config.get_j3_channel(group_id), 270)


def set_all_j1(angle):
    for group_id in leg_config.CONNECTED_LEGS:
        legs_j1[group_id].angle = leg_config.apply_offset(angle, group_id, "j1")


def set_all_j2_j3(j2_angle, j3_angle):
    for group_id in leg_config.CONNECTED_LEGS:
        legs_j2[group_id].angle = leg_config.apply_offset(j2_angle, group_id, "j2")
        legs_j3[group_id].angle = leg_config.apply_offset(j3_angle, group_id, "j3")


def smooth_j1(start, end):
    """全脚の J1 を start から end まで滑らかに動かす"""
    step = STEP_DEGREES if end > start else -STEP_DEGREES
    for angle in range(start, end + step, step):
        set_all_j1(angle)
        time.sleep(STEP_DELAY)


def smooth_j2_j3(j2_start, j2_end, j3_start, j3_end):
    """J2 と J3 を同時に滑らかに動かす"""
    j2_step = STEP_DEGREES if j2_end > j2_start else -STEP_DEGREES
    j3_step = STEP_DEGREES if j3_end > j3_start else -STEP_DEGREES
    # ステップ数を揃える
    j2_steps = abs(j2_end - j2_start)
    j3_steps = abs(j3_end - j3_start)
    n_steps = max(j2_steps, j3_steps)
    for i in range(n_steps + 1):
        j2 = j2_start + j2_step * min(i, j2_steps)
        j3 = j3_start + j3_step * min(i, j3_steps)
        set_all_j2_j3(j2, j3)
        time.sleep(STEP_DELAY)


legs_str = [leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]
print(f"対象の脚: {legs_str}")

try:
    print("\n[1/7] 休眠姿勢にリセット")
    set_all_j1(J1_NEUTRAL)
    time.sleep(0.3)
    set_all_j2_j3(J2_NEUTRAL, J3_NEUTRAL)
    time.sleep(1)

    j2_up = J2_NEUTRAL + J2_DIR * LIFT_DEGREES
    j3_up = J3_NEUTRAL + J3_DIR * LIFT_DEGREES

    print(f"[2/7] 立ち上がり (J2={j2_up}度, J3={j3_up}度)")
    smooth_j2_j3(J2_NEUTRAL, j2_up, J3_NEUTRAL, j3_up)
    time.sleep(HOLD_TIME)

    j1_left = J1_NEUTRAL + ROTATE_DEGREES
    j1_right = J1_NEUTRAL - ROTATE_DEGREES

    print(f"[3/7] 左に回転 (J1={j1_left}度)")
    smooth_j1(J1_NEUTRAL, j1_left)
    time.sleep(HOLD_TIME)

    print(f"[4/7] 中央に戻す (J1={J1_NEUTRAL}度)")
    smooth_j1(j1_left, J1_NEUTRAL)
    time.sleep(HOLD_TIME)

    print(f"[5/7] 右に回転 (J1={j1_right}度)")
    smooth_j1(J1_NEUTRAL, j1_right)
    time.sleep(HOLD_TIME)

    print(f"[6/7] 中央に戻す (J1={J1_NEUTRAL}度)")
    smooth_j1(j1_right, J1_NEUTRAL)
    time.sleep(HOLD_TIME)

    print(f"[7/7] 着地 (J2={J2_NEUTRAL}度, J3={J3_NEUTRAL}度)")
    smooth_j2_j3(j2_up, J2_NEUTRAL, j3_up, J3_NEUTRAL)

except KeyboardInterrupt:
    print("\n中断 - 休眠姿勢に戻します")
    set_all_j1(J1_NEUTRAL)
    set_all_j2_j3(J2_NEUTRAL, J3_NEUTRAL)

pca.deinit()
print("完了")
