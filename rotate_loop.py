"""立ち上がった状態で J1 回転のみ (屈伸なし) を繰り返すテスト。

body_height_test.py から立ち上がり処理と回転パラメータを流用。
Ctrl+C で停止すると休眠姿勢に戻る。

シーケンス:
  1. 休眠姿勢
  2. 立ち上がり (標準高さ)
  3. 右回転 -> 中央 -> 左回転 -> 中央 を無限ループ
  4. (中断時) 着地して休眠姿勢
"""
import time

import leg_config

# 中立角度 (rest 状態)
J1_NEUTRAL = 90
J2_NEUTRAL = 135
J3_NEUTRAL = 135

# 立ち上がり量 (J2 を曲げ, J3 を伸ばす)
LIFT_DEGREES = 40
J2_DIR = -1
J3_DIR = +1

# 回転量 (J1 の中立からのオフセット)
# + が右回転、- が左回転 (機構次第なので必要なら符号を反転)
ROTATE_DEGREES = 25

# 動作の細かさ
STEP_DEGREES = 1
STEP_DELAY = 0.03
HOLD_TIME = 0.5


def set_all(j1_angle, j2_angle, j3_angle):
    """全脚の 3 サーボを同時に同じ角度に設定 (オフセット適用済み)"""
    for group_id in leg_config.CONNECTED_LEGS:
        leg_config.set_angle(group_id, "j1", j1_angle)
        leg_config.set_angle(group_id, "j2", j2_angle)
        leg_config.set_angle(group_id, "j3", j3_angle)


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


def rotate_only(j1_start, j1_end, j2, j3):
    """J2/J3 は固定したまま J1 だけ動かす。"""
    smooth_move(j1_start, j1_end, j2, j2, j3, j3)


legs_str = [leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]
print(f"対象の脚: {legs_str}")

# 標準の立ち上がり姿勢
j2_stand = J2_NEUTRAL + J2_DIR * LIFT_DEGREES
j3_stand = J3_NEUTRAL + J3_DIR * LIFT_DEGREES

# 回転位置
j1_right = J1_NEUTRAL - ROTATE_DEGREES
j1_left = J1_NEUTRAL + ROTATE_DEGREES

print(f"立ち姿勢: J1={J1_NEUTRAL}, J2={j2_stand}, J3={j3_stand}")
print(f"回転: 右={j1_right}, 左={j1_left}")

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

    print("[3] 回転動作をループ (Ctrl+C で停止)")
    j1_current = J1_NEUTRAL
    while True:
        rotate_only(j1_current, j1_right, j2_stand, j3_stand)
        time.sleep(HOLD_TIME)
        rotate_only(j1_right, J1_NEUTRAL, j2_stand, j3_stand)
        time.sleep(HOLD_TIME)
        rotate_only(J1_NEUTRAL, j1_left, j2_stand, j3_stand)
        time.sleep(HOLD_TIME)
        rotate_only(j1_left, J1_NEUTRAL, j2_stand, j3_stand)
        time.sleep(HOLD_TIME)
        j1_current = J1_NEUTRAL

except KeyboardInterrupt:
    print("\n中断 - 着地して休眠姿勢に戻します")
    smooth_move(
        j1_current, J1_NEUTRAL,
        j2_stand, J2_NEUTRAL,
        j3_stand, J3_NEUTRAL,
    )
    set_all(J1_NEUTRAL, J2_NEUTRAL, J3_NEUTRAL)

leg_config.deinit()
print("完了")
