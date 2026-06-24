"""展示用: 省電力で立ち上がり、トルクを切ってポーズを維持するスクリプト。

efficient_stand_up.py の省電力な立ち上がり (同時駆動サーボを 3 個までに
抑える 3 ステップ方式) を流用する。違いは 2 点:

  1. 立ち姿勢に達したら deinit() でトルクを切る。
     サーボへの信号が止まるので保持電力ゼロ・発熱なし。機構の保持トルクで
     ポーズを維持する (展示向け)。
  2. 着地はしない。Ctrl+C / 終了時もその場で停止する (既に deinit 済み)。

立ち上がり手順 (efficient_stand_up.py と同じ):
  STEP A:  J3 を + 方向に動かして足先を地面に近づける (J2 は維持)
  STEP B1: J3 をさらに + 方向に動かして足先を強く接地させる
  STEP B2: J2 を - 方向に動かして胴体を持ち上げる (動作幅を 2 分割)
"""
import time

import leg_config

# 中立角度 (rest 状態)
J2_NEUTRAL = 135
J3_NEUTRAL = 135

# 立ち姿勢 (中立からの相対量)
LIFT_DEGREES = 40
J2_DIR = -1
J3_DIR = +1

# STEP A: 準備姿勢 (J3 だけを動かして足先を地面に近づける)
PREP_J3_DEGREES = 30

# 電源モード
# "battery": モバイルバッテリー (5V/3A = 15W) 制約あり。動作は控えめに。
# "adapter": 5V ACアダプタや DC-DC 経由 (~25-30W) で余裕あり。速めに。
POWER_MODE = "battery"

_POWER_PARAMS = {
    "battery": {
        "STEP_DELAY": 0.08,
        "BETWEEN_PHASE_DELAY": 0.3,
    },
    "adapter": {
        "STEP_DELAY": 0.05,
        "BETWEEN_PHASE_DELAY": 0.2,
    },
}

# 動作の細かさ
STEP_DEGREES = 1
STEP_DELAY = _POWER_PARAMS[POWER_MODE]["STEP_DELAY"]
BETWEEN_PHASE_DELAY = _POWER_PARAMS[POWER_MODE]["BETWEEN_PHASE_DELAY"]
# 立ち姿勢に達した後、トルクを切る前に姿勢を安定させる待ち時間
SETTLE_TIME = 1.5


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


legs_str = [leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]
print(f"対象の脚: {legs_str}")
print(f"電源モード: {POWER_MODE} (STEP_DELAY={STEP_DELAY}, BETWEEN_PHASE_DELAY={BETWEEN_PHASE_DELAY})")

# 立ち姿勢
j2_stand = J2_NEUTRAL + J2_DIR * LIFT_DEGREES
j3_stand = J3_NEUTRAL + J3_DIR * LIFT_DEGREES

# 準備姿勢 (J2 は中立のまま、J3 だけ + 方向)
j2_prep = J2_NEUTRAL
j3_prep = J3_NEUTRAL + PREP_J3_DEGREES

# STEP B2 の中間点 (J2 の動作幅を半分に分割して初期加速ピークを下げる)
j2_mid = (j2_prep + j2_stand) // 2

print(f"休眠姿勢:    J2={J2_NEUTRAL}, J3={J3_NEUTRAL}")
print(f"準備姿勢:    J2={j2_prep}, J3={j3_prep}")
print(f"B2 中間点:   J2={j2_mid}")
print(f"立ち姿勢:    J2={j2_stand}, J3={j3_stand}")

try:
    print("\n[1] 休眠姿勢にリセット")
    set_all(J2_NEUTRAL, J3_NEUTRAL)
    time.sleep(1)

    print("[2] STEP A: J3 を曲げて準備姿勢へ (J2 は維持)")
    smooth_move(J2_NEUTRAL, j2_prep, J3_NEUTRAL, j3_prep)
    time.sleep(BETWEEN_PHASE_DELAY)

    print("[3] STEP B1: J3 をさらに伸ばす (J2 は維持)")
    smooth_move(j2_prep, j2_prep, j3_prep, j3_stand)
    time.sleep(BETWEEN_PHASE_DELAY)

    print("[4a] STEP B2a: J2 を中間点まで動かす")
    smooth_move(j2_prep, j2_mid, j3_stand, j3_stand)
    time.sleep(BETWEEN_PHASE_DELAY)

    print("[4b] STEP B2b: J2 を立ち姿勢まで動かす")
    smooth_move(j2_mid, j2_stand, j3_stand, j3_stand)

    print(f"[5] 立ち姿勢で {SETTLE_TIME} 秒安定させます")
    time.sleep(SETTLE_TIME)

    print("[6] トルクを切ります (保持電力ゼロ・発熱なし)")
    print("    機構の保持トルクでポーズを維持します")
    leg_config.deinit()
    print("\n展示準備完了。サーボはトルクオフです。")
    print("姿勢が崩れる場合は POWER_MODE や LIFT_DEGREES の調整、")
    print("または保持トルクが足りない関節の見直しが必要です。")

except KeyboardInterrupt:
    print("\n中断されました - その場で停止 (トルクを切ります)")
    leg_config.deinit()

print("完了")
