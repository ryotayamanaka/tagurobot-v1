"""屈伸動作 (スクワット) + 回転の組み合わせテスト。

エンドエフェクターの地面に対する角度を維持しながら胴体だけ上下する。
立ち姿勢から J2 を戻す方向、J3 をさらに曲げる方向 (両方とも +方向)
に同じ量だけ動かすと、足先の向きを保ちつつ胴体が下がる。

2 回目以降の屈伸では J1 も同時に動かして、かがみながら回転 ->
立ち上がりながら正面に戻る、という動きを行う。

シーケンス:
  1. 休眠姿勢
  2. 立ち上がり (標準高さ)
  3-1. 屈伸のみ (回転なし)
  3-2. 屈伸 + 右回転
  3-3. 屈伸 + 左回転
  4. 着地
"""
import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

import leg_config

# 中立角度 (rest 状態)
J1_NEUTRAL = 90
J2_NEUTRAL = 90
J3_NEUTRAL = 135

# 立ち上がり量 (J2 を曲げ, J3 を伸ばす)
LIFT_DEGREES = 40
J2_DIR = -1
J3_DIR = +1

# かがみの深さ
SQUAT_DEGREES = 40

# 回転量 (J1 の中立からのオフセット)
# + が右回転、- が左回転 (機構次第なので必要なら符号を反転)
ROTATE_DEGREES = 25

# 動作の細かさ
STEP_DEGREES = 1
STEP_DELAY = 0.04
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


legs_j1 = {}
legs_j2 = {}
legs_j3 = {}
for group_id in leg_config.CONNECTED_LEGS:
    legs_j1[group_id] = make_servo(leg_config.get_j1_channel(group_id), 180)
    legs_j2[group_id] = make_servo(leg_config.get_j2_channel(group_id), 180)
    legs_j3[group_id] = make_servo(leg_config.get_j3_channel(group_id), 270)


def set_all(j1_angle, j2_angle, j3_angle):
    """全脚の 3 サーボを同時に同じ角度に設定 (オフセット適用済み)"""
    for group_id in leg_config.CONNECTED_LEGS:
        legs_j1[group_id].angle = leg_config.apply_offset(j1_angle, group_id, "j1")
        legs_j2[group_id].angle = leg_config.apply_offset(j2_angle, group_id, "j2")
        legs_j3[group_id].angle = leg_config.apply_offset(j3_angle, group_id, "j3")


def smooth_move(j1_start, j1_end, j2_start, j2_end, j3_start, j3_end):
    """3 サーボを同時に滑らかに動かす。最大の差分に合わせてステップ数を決める。"""
    j1_step = STEP_DEGREES if j1_end >= j1_start else -STEP_DEGREES
    j2_step = STEP_DEGREES if j2_end >= j2_start else -STEP_DEGREES
    j3_step = STEP_DEGREES if j3_end >= j3_start else -STEP_DEGREES
    j1_steps = abs(j1_end - j1_start)
    j2_steps = abs(j2_end - j2_start)
    j3_steps = abs(j3_end - j3_start)
    n_steps = max(j1_steps, j2_steps, j3_steps)
    for i in range(n_steps + 1):
        j1 = j1_start + j1_step * min(i, j1_steps)
        j2 = j2_start + j2_step * min(i, j2_steps)
        j3 = j3_start + j3_step * min(i, j3_steps)
        set_all(j1, j2, j3)
        time.sleep(STEP_DELAY)


legs_str = [leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]
print(f"対象の脚: {legs_str}")

# 標準の立ち上がり姿勢
j2_stand = J2_NEUTRAL + J2_DIR * LIFT_DEGREES
j3_stand = J3_NEUTRAL + J3_DIR * LIFT_DEGREES

# かがみ姿勢
j2_squat = j2_stand + SQUAT_DEGREES
j3_squat = j3_stand + SQUAT_DEGREES

# 回転位置
j1_right = J1_NEUTRAL - ROTATE_DEGREES
j1_left = J1_NEUTRAL + ROTATE_DEGREES

print(f"立ち姿勢:    J1={J1_NEUTRAL}, J2={j2_stand}, J3={j3_stand}")
print(f"かがみ姿勢:  J2={j2_squat}, J3={j3_squat}")
print(f"回転: 右={j1_right}, 左={j1_left}")


def squat_with_rotation(j1_target):
    """屈伸 (かがむ -> 立つ) を実行する。
    かがむ時に J1 を j1_target に、立つ時に J1_NEUTRAL に戻す。
    j1_target = J1_NEUTRAL なら回転なしの純粋な屈伸。
    """
    smooth_move(
        J1_NEUTRAL, j1_target,
        j2_stand, j2_squat,
        j3_stand, j3_squat,
    )
    time.sleep(HOLD_TIME)
    smooth_move(
        j1_target, J1_NEUTRAL,
        j2_squat, j2_stand,
        j3_squat, j3_stand,
    )
    time.sleep(HOLD_TIME)


try:
    print("\n[1] 休眠姿勢にリセット")
    set_all(J1_NEUTRAL, J2_NEUTRAL, J3_NEUTRAL)
    time.sleep(1)

    print("[2] 立ち上がり")
    smooth_move(
        J1_NEUTRAL, J1_NEUTRAL,
        J2_NEUTRAL, j2_stand,
        J3_NEUTRAL, j3_stand,
    )
    time.sleep(HOLD_TIME)

    print("[3-1] 屈伸のみ")
    squat_with_rotation(J1_NEUTRAL)

    print("[3-2] 屈伸 + 右回転")
    squat_with_rotation(j1_right)

    print("[3-3] 屈伸 + 左回転")
    squat_with_rotation(j1_left)

    print("[4] 着地")
    smooth_move(
        J1_NEUTRAL, J1_NEUTRAL,
        j2_stand, J2_NEUTRAL,
        j3_stand, J3_NEUTRAL,
    )

except KeyboardInterrupt:
    print("\n中断 - 休眠姿勢に戻します")
    set_all(J1_NEUTRAL, J2_NEUTRAL, J3_NEUTRAL)

pca.deinit()
print("完了")
