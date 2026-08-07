"""既に立ち上がっている状態から、J1 回転 + 軽い屈伸を繰り返すテスト。

立ち上がり動作は行わない。実行前に別途立ち上がらせておくこと
(例: efficient_stand_up.py や body_height_test.py の [2] 相当)。
実行開始時点の姿勢を「立ち姿勢」(J2_STAND/J3_STAND) とみなし、そこから
J1 を回転させながら少しだけかがみ、中央に戻るときに立ち上がる。

シーケンス (body_height_test.py の [3-2][3-3] に相当):
  1. 立ち姿勢からかがみながら右回転 -> 立ちながら中央に戻る
  2. 立ち姿勢からかがみながら左回転 -> 立ちながら中央に戻る
  を無限ループ
  3. (中断時) J1・J2・J3 を立ち姿勢に戻す
"""
import time

import leg_config

# 中立角度 (J1 の中央)
J1_NEUTRAL = 90

# 実行開始時点の姿勢を立ち姿勢とみなす (J2/J3 の基準値)
# 270°化に伴う中立 135° からの相対量。body_height_test.py の標準立ち上がり
# (J2_DIR=-1, J3_DIR=+1, LIFT_DEGREES=40) と揃えてある。
J2_STAND = 135 - 40
J3_STAND = 135 + 40

# 回転量 (J1 の中立からのオフセット)
# + が右回転、- が左回転 (機構次第なので必要なら符号を反転)
ROTATE_DEGREES = 25

# 屈伸の深さ (立ち姿勢からさらにかがむ量)
SQUAT_DEGREES = 15

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


legs_str = [leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]
print(f"対象の脚: {legs_str}")

# かがみ姿勢
j2_squat = J2_STAND + SQUAT_DEGREES
j3_squat = J3_STAND + SQUAT_DEGREES

# 回転位置
j1_right = J1_NEUTRAL - ROTATE_DEGREES
j1_left = J1_NEUTRAL + ROTATE_DEGREES

print(f"立ち姿勢: J1={J1_NEUTRAL}, J2={J2_STAND}, J3={J3_STAND}")
print(f"かがみ姿勢: J2={j2_squat}, J3={j3_squat}")
print(f"回転: 右={j1_right}, 左={j1_left}")
print("既に立ち上がっている前提で回転+屈伸を行います")


def squat_with_rotation(j1_target):
    """かがみながら J1 を j1_target へ、立ちながら J1_NEUTRAL に戻す。"""
    smooth_move(
        J1_NEUTRAL, j1_target,
        J2_STAND, j2_squat,
        J3_STAND, j3_squat,
    )
    time.sleep(HOLD_TIME)
    smooth_move(
        j1_target, J1_NEUTRAL,
        j2_squat, J2_STAND,
        j3_squat, J3_STAND,
    )
    time.sleep(HOLD_TIME)


try:
    print("\n[1] 回転+屈伸をループ (Ctrl+C で停止)")
    while True:
        squat_with_rotation(j1_right)
        squat_with_rotation(j1_left)

except KeyboardInterrupt:
    print("\n中断 - 立ち姿勢に戻します")
    smooth_move(
        J1_NEUTRAL, J1_NEUTRAL,
        J2_STAND, J2_STAND,
        J3_STAND, J3_STAND,
    )

leg_config.deinit()
print("完了")
