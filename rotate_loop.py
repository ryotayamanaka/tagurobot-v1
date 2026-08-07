"""既に立ち上がっている状態から、J1 回転のみ (屈伸なし) を繰り返すテスト。

立ち上がり動作は行わない。実行前に別途立ち上がらせておくこと
(例: efficient_stand_up.py や body_height_test.py の [2] 相当)。
J2/J3 は一切動かさず、現在の立ち姿勢を保ったまま J1 だけを動かす。
Ctrl+C で停止すると J1 を中央に戻して終了する (J2/J3 はそのまま)。

シーケンス:
  1. 右回転 -> 中央 -> 左回転 -> 中央 を無限ループ
  2. (中断時) J1 を中央に戻す
"""
import time

import leg_config

# 中立角度 (J1 の中央)
J1_NEUTRAL = 90

# 回転量 (J1 の中立からのオフセット)
# + が右回転、- が左回転 (機構次第なので必要なら符号を反転)
ROTATE_DEGREES = 25

# 動作の細かさ
STEP_DEGREES = 1
STEP_DELAY = 0.03
HOLD_TIME = 0.5


def set_j1_all(j1_angle):
    """全脚の J1 サーボを同時に同じ角度に設定 (オフセット適用済み)。J2/J3 には触れない。"""
    for group_id in leg_config.CONNECTED_LEGS:
        leg_config.set_angle(group_id, "j1", j1_angle)


def rotate_only(j1_start, j1_end):
    """J1 のみを滑らかに動かす。J2/J3 は現状維持。"""
    j1_step = STEP_DEGREES if j1_end >= j1_start else -STEP_DEGREES
    n_steps = abs(j1_end - j1_start)
    for i in range(n_steps + 1):
        j1 = j1_start + j1_step * i
        set_j1_all(j1)
        time.sleep(STEP_DELAY)


legs_str = [leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]
print(f"対象の脚: {legs_str}")

# 回転位置
j1_right = J1_NEUTRAL - ROTATE_DEGREES
j1_left = J1_NEUTRAL + ROTATE_DEGREES

print(f"中央: J1={J1_NEUTRAL} / 回転: 右={j1_right}, 左={j1_left}")
print("既に立ち上がっている前提で J1 回転のみを行います (J2/J3 は動かしません)")

j1_current = J1_NEUTRAL

try:
    print("\n[1] 回転動作をループ (Ctrl+C で停止)")
    while True:
        rotate_only(j1_current, j1_right)
        j1_current = j1_right
        time.sleep(HOLD_TIME)
        rotate_only(j1_current, J1_NEUTRAL)
        j1_current = J1_NEUTRAL
        time.sleep(HOLD_TIME)
        rotate_only(j1_current, j1_left)
        j1_current = j1_left
        time.sleep(HOLD_TIME)
        rotate_only(j1_current, J1_NEUTRAL)
        j1_current = J1_NEUTRAL
        time.sleep(HOLD_TIME)

except KeyboardInterrupt:
    print("\n中断 - J1 を中央に戻します (J2/J3 はそのまま)")
    rotate_only(j1_current, J1_NEUTRAL)

leg_config.deinit()
print("完了")
