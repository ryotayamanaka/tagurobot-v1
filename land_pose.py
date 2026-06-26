"""立ち姿勢から休眠姿勢へ省電力・低衝撃で着地するスクリプト。

exhibit_pose.py / efficient_stand_up.py で立たせた状態から、安全に
足を下ろして休眠姿勢 (足まっすぐ) に戻す。

立ち姿勢からいきなり rest_position.py で全関節を中立へ一斉移動すると、
胴体が急に落ちて崩れる恐れがある。ここでは efficient_stand_up.py の
着地ロジック (立ち上がりの逆順) を流用し、同時に動くサーボを 3 個までに
抑えつつ段階的に下ろす:

  STEP B2 逆: J2 を立ち姿勢 -> 準備姿勢へ (2 分割で初期衝撃を下げる)
  STEP B1 逆: J3 を立ち姿勢 -> 準備姿勢へ
  STEP A 逆:  J3 を準備姿勢 -> 中立へ (休眠姿勢)

前提: 立ち姿勢 (J2=95, J3=175 付近) で接地していること。
"""
import time

import leg_config

# 中立角度 (rest 状態) — efficient_stand_up.py と同じ
J2_NEUTRAL = 135
J3_NEUTRAL = 135

# 立ち姿勢 (中立からの相対量) — efficient_stand_up.py と同じ
LIFT_DEGREES = 40
J2_DIR = -1
J3_DIR = +1

# STEP A: 準備姿勢 (J3 だけ + 方向、J2 は中立)
PREP_J3_DEGREES = 30

# 電源モード (efficient_stand_up.py と同じ流儀)
POWER_MODE = "battery"
_POWER_PARAMS = {
    "battery": {"STEP_DELAY": 0.08, "BETWEEN_PHASE_DELAY": 0.3},
    "adapter": {"STEP_DELAY": 0.05, "BETWEEN_PHASE_DELAY": 0.2},
}

STEP_DEGREES = 1
STEP_DELAY = _POWER_PARAMS[POWER_MODE]["STEP_DELAY"]
BETWEEN_PHASE_DELAY = _POWER_PARAMS[POWER_MODE]["BETWEEN_PHASE_DELAY"]


def set_all(j2_angle, j3_angle):
    """全脚の J2 と J3 を同時に同じ角度に設定 (オフセット適用済み)"""
    for group_id in leg_config.CONNECTED_LEGS:
        leg_config.set_angle(group_id, "j2", j2_angle)
        leg_config.set_angle(group_id, "j3", j3_angle)


def smooth_move(j2_start, j2_end, j3_start, j3_end):
    """J2 と J3 を同時に滑らかに動かす"""
    j2_step = STEP_DEGREES if j2_end >= j2_start else -STEP_DEGREES
    j3_step = STEP_DEGREES if j3_end >= j3_start else -STEP_DEGREES
    j2_steps = abs(j2_end - j2_start)
    j3_steps = abs(j3_end - j3_start)
    n_steps = max(j2_steps, j3_steps)
    for i in range(n_steps + 1):
        j2 = j2_start + j2_step * min(i, j2_steps)
        j3 = j3_start + j3_step * min(i, j3_steps)
        set_all(j2, j3)
        time.sleep(STEP_DELAY)


# 立ち姿勢
j2_stand = J2_NEUTRAL + J2_DIR * LIFT_DEGREES
j3_stand = J3_NEUTRAL + J3_DIR * LIFT_DEGREES
# 準備姿勢 (J2 は中立、J3 だけ + 方向)
j2_prep = J2_NEUTRAL
j3_prep = J3_NEUTRAL + PREP_J3_DEGREES
# STEP B2 の中間点 (J2 の動作幅を半分に分割)
j2_mid = (j2_prep + j2_stand) // 2

legs_str = [leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]
print(f"対象の脚: {legs_str}")
print(f"電源モード: {POWER_MODE} (STEP_DELAY={STEP_DELAY}, BETWEEN_PHASE_DELAY={BETWEEN_PHASE_DELAY})")
print(f"立ち姿勢:    J2={j2_stand}, J3={j3_stand}")
print(f"準備姿勢:    J2={j2_prep}, J3={j3_prep}")
print(f"休眠姿勢:    J2={J2_NEUTRAL}, J3={J3_NEUTRAL}")
print("\n前提: 立ち姿勢で接地していること")

try:
    print("\n[1] STEP B2b 逆: J2 を中間点まで戻す")
    smooth_move(j2_stand, j2_mid, j3_stand, j3_stand)
    time.sleep(BETWEEN_PHASE_DELAY)

    print("[2] STEP B2a 逆: J2 を準備姿勢まで戻す")
    smooth_move(j2_mid, j2_prep, j3_stand, j3_stand)
    time.sleep(BETWEEN_PHASE_DELAY)

    print("[3] STEP B1 逆: J3 を準備姿勢まで戻す")
    smooth_move(j2_prep, j2_prep, j3_stand, j3_prep)
    time.sleep(BETWEEN_PHASE_DELAY)

    print("[4] STEP A 逆: J3 を中立まで戻して休眠姿勢へ")
    smooth_move(j2_prep, J2_NEUTRAL, j3_prep, J3_NEUTRAL)

    print("\n休眠姿勢に戻りました")

except KeyboardInterrupt:
    print("\n中断 - 休眠姿勢に戻します")
    set_all(J2_NEUTRAL, J3_NEUTRAL)

leg_config.deinit()
print("完了")
