"""立った状態で足先位置をほぼ維持したまま胴体だけを上下させるテスト。

J2 と J3 を反対方向に同じ量だけ動かすと、近似的に足先が同じ位置に
留まったまま胴体高さが変わる (簡易版、厳密な逆運動学は使わない)。

シーケンス:
  1. 休眠姿勢
  2. 立ち上がり (標準高さ)
  3. 胴体を上げる (J2 さらに曲げる, J3 さらに伸ばす)
  4. 標準高さに戻る
  5. 胴体を下げる (J2 伸ばす, J3 曲げる)
  6. 標準高さに戻る
  7. 着地
"""
import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

import leg_config

# 中立角度 (rest 状態)
J2_NEUTRAL = 90
J3_NEUTRAL = 135

# 立ち上がり量 (J2 を曲げ, J3 を伸ばす)
LIFT_DEGREES = 40
J2_DIR = -1
J3_DIR = +1

# 胴体高さの増分 (立ち上がった状態を中心に, ±この量で上下する)
# J2 と J3 を反対方向に同じ量動かす
HEIGHT_DEGREES = 10

# 動作の細かさ
STEP_DEGREES = 1
STEP_DELAY = 0.08
HOLD_TIME = 1.0

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


legs_j2 = {}
legs_j3 = {}
for group_id in leg_config.CONNECTED_LEGS:
    legs_j2[group_id] = make_servo(leg_config.get_j2_channel(group_id), 180)
    legs_j3[group_id] = make_servo(leg_config.get_j3_channel(group_id), 270)


def set_all(j2_angle, j3_angle):
    """全脚の J2 と J3 を同時に同じ角度に設定 (オフセット適用済み)"""
    for group_id in leg_config.CONNECTED_LEGS:
        legs_j2[group_id].angle = leg_config.apply_offset(j2_angle, group_id, "j2")
        legs_j3[group_id].angle = leg_config.apply_offset(j3_angle, group_id, "j3")


def smooth_move(j2_start, j2_end, j3_start, j3_end):
    """J2 と J3 を同時に滑らかに動かす"""
    j2_step = STEP_DEGREES if j2_end > j2_start else -STEP_DEGREES
    j3_step = STEP_DEGREES if j3_end > j3_start else -STEP_DEGREES
    j2_steps = abs(j2_end - j2_start)
    j3_steps = abs(j3_end - j3_start)
    n_steps = max(j2_steps, j3_steps)
    for i in range(n_steps + 1):
        j2 = j2_start + j2_step * min(i, j2_steps)
        j3 = j3_start + j3_step * min(i, j3_steps)
        set_all(j2, j3)
        time.sleep(STEP_DELAY)


legs_str = [leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]
print(f"対象の脚: {legs_str}")

# 標準の立ち上がり姿勢
j2_stand = J2_NEUTRAL + J2_DIR * LIFT_DEGREES
j3_stand = J3_NEUTRAL + J3_DIR * LIFT_DEGREES

# 高い姿勢 (J2 をさらに曲げる, J3 をさらに伸ばす)
j2_high = j2_stand + J2_DIR * HEIGHT_DEGREES
j3_high = j3_stand + J3_DIR * HEIGHT_DEGREES

# 低い姿勢 (J2 を伸ばす, J3 を曲げる)
j2_low = j2_stand - J2_DIR * HEIGHT_DEGREES
j3_low = j3_stand - J3_DIR * HEIGHT_DEGREES

print(f"標準姿勢: J2={j2_stand}, J3={j3_stand}")
print(f"高い姿勢: J2={j2_high}, J3={j3_high}")
print(f"低い姿勢: J2={j2_low}, J3={j3_low}")

try:
    print("\n[1/7] 休眠姿勢にリセット")
    set_all(J2_NEUTRAL, J3_NEUTRAL)
    time.sleep(1)

    print("[2/7] 立ち上がり")
    smooth_move(J2_NEUTRAL, j2_stand, J3_NEUTRAL, j3_stand)
    time.sleep(HOLD_TIME)

    print("[3/7] 胴体を上げる")
    smooth_move(j2_stand, j2_high, j3_stand, j3_high)
    time.sleep(HOLD_TIME)

    print("[4/7] 標準高さに戻る")
    smooth_move(j2_high, j2_stand, j3_high, j3_stand)
    time.sleep(HOLD_TIME)

    print("[5/7] 胴体を下げる")
    smooth_move(j2_stand, j2_low, j3_stand, j3_low)
    time.sleep(HOLD_TIME)

    print("[6/7] 標準高さに戻る")
    smooth_move(j2_low, j2_stand, j3_low, j3_stand)
    time.sleep(HOLD_TIME)

    print("[7/7] 着地")
    smooth_move(j2_stand, J2_NEUTRAL, j3_stand, J3_NEUTRAL)

except KeyboardInterrupt:
    print("\n中断 - 休眠姿勢に戻します")
    set_all(J2_NEUTRAL, J3_NEUTRAL)

pca.deinit()
print("完了")
