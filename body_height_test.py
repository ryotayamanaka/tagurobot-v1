"""立った状態と屈んだ状態を行き来する屈伸動作 (スクワット) のテスト。

エンドエフェクターの地面に対する角度を維持しながら胴体だけ上下する。
立ち姿勢から J2 を戻す方向、J3 をさらに曲げる方向 (両方とも +方向)
に同じ量だけ動かすと、足先の向きを保ちつつ胴体が下がる。

シーケンス:
  1. 休眠姿勢
  2. 立ち上がり (標準高さ)
  3. 屈伸 (かがむ -> 立つ) を 3 回繰り返す
  4. 着地
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

# かがみの深さ (立った位置から下に向かう量)
# J2 を立ち姿勢から戻す方向に、J3 を縮める方向に動かす
SQUAT_DEGREES = 30

# 繰り返し回数
SQUAT_CYCLES = 3

# 動作の細かさ
STEP_DEGREES = 1
STEP_DELAY = 0.05
HOLD_TIME = 0.5

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

# かがんだ姿勢
# J2 は立ち姿勢から戻す方向 (+) = 中立寄りに伸ばす
# J3 はさらに曲げる方向 (+) = エンドエフェクターの地面に対する角度を維持
j2_squat = j2_stand + SQUAT_DEGREES
j3_squat = j3_stand + SQUAT_DEGREES

print(f"立ち姿勢:    J2={j2_stand}, J3={j3_stand}")
print(f"かがみ姿勢:  J2={j2_squat}, J3={j3_squat}")

try:
    print("\n[1] 休眠姿勢にリセット")
    set_all(J2_NEUTRAL, J3_NEUTRAL)
    time.sleep(1)

    print("[2] 立ち上がり")
    smooth_move(J2_NEUTRAL, j2_stand, J3_NEUTRAL, j3_stand)
    time.sleep(HOLD_TIME)

    for i in range(SQUAT_CYCLES):
        print(f"[3-{i+1}/{SQUAT_CYCLES}] かがむ")
        smooth_move(j2_stand, j2_squat, j3_stand, j3_squat)
        time.sleep(HOLD_TIME)

        print(f"[3-{i+1}/{SQUAT_CYCLES}] 立つ")
        smooth_move(j2_squat, j2_stand, j3_squat, j3_stand)
        time.sleep(HOLD_TIME)

    print("[4] 着地")
    smooth_move(j2_stand, J2_NEUTRAL, j3_stand, J3_NEUTRAL)

except KeyboardInterrupt:
    print("\n中断 - 休眠姿勢に戻します")
    set_all(J2_NEUTRAL, J3_NEUTRAL)

pca.deinit()
print("完了")
