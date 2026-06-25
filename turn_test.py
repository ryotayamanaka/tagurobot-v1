"""6脚 tripod 旋回テスト (その場で回る)。

放射状配置 (上から見て時計回りに A,B,C,D,E,F) では、全脚を同じ J1 方向に
振ると機体はその場で旋回する。直進は脚ごとの運動学が要るが、旋回は不要。

tripod gait: 脚を 1 つおきに 2 グループへ分ける。
  グループ1 = A,C,E (group_id 0,2,4)
  グループ2 = B,D,F (group_id 1,3,5)
片方を接地させて J1 で蹴る間、もう片方を持ち上げて反対へ振り戻す。
常に 3 脚接地なので安定する。

前提: 既に立ち姿勢で接地していること (efficient_stand_up.py で立たせてから実行)。
このスクリプトは J2/J3 を立ち姿勢に保ち、J1 だけを動かして旋回する。

安全のため efficient_stand_up と同じく「同時に動かすのは 3 脚まで」を守る
(tripod の 1 グループ = 3 脚)。電力ピークが問題なら STEP_DELAY を増やす。
"""
import time

import leg_config

# 立ち姿勢 (efficient_stand_up.py と同じ値)。J2/J3 はこの姿勢を保つ。
J2_NEUTRAL = 135
J3_NEUTRAL = 135
LIFT_DEGREES = 40
J2_STAND = J2_NEUTRAL - LIFT_DEGREES   # 95
J3_STAND = J3_NEUTRAL + LIFT_DEGREES   # 175

# J1 (脚の前後/旋回方向の振り)
J1_NEUTRAL = 90
SWING = 25          # J1 を中立から ± この量振る (旋回の歩幅)
LIFT_FOR_SWING = 25 # 遊脚を持ち上げる量 (J3 を縮めて足先を浮かせる)

# tripod の 2 グループ (放射状配置で 1 つおき)
GROUP_1 = [g for g in (0, 2, 4) if g in leg_config.CONNECTED_LEGS]
GROUP_2 = [g for g in (1, 3, 5) if g in leg_config.CONNECTED_LEGS]

# 旋回方向: +1 で全脚 J1 を + 方向に蹴る (機体は一方向に回る)。-1 で逆回り。
TURN_DIR = +1

# 動作パラメータ
STEP_DEGREES = 1
STEP_DELAY = 0.02
PHASE_DELAY = 0.15
CYCLES = 6


def set_stand(group):
    """指定グループの脚を立ち姿勢の J2/J3 に保つ (接地)。"""
    for g in group:
        leg_config.set_angle(g, "j2", J2_STAND)
        leg_config.set_angle(g, "j3", J3_STAND)


def set_j1(group, angle):
    for g in group:
        leg_config.set_angle(g, "j1", angle)


def smooth_j1(group, start, end):
    """グループの J1 を滑らかに動かす。"""
    step = STEP_DEGREES if end >= start else -STEP_DEGREES
    for a in range(start, end + step, step):
        set_j1(group, a)
        time.sleep(STEP_DELAY)


def lift_group(group, lifted):
    """遊脚グループを持ち上げる (lifted=True) / 下ろす (False)。J3 を縮めて浮かす。"""
    j3 = J3_STAND - LIFT_FOR_SWING if lifted else J3_STAND
    for g in group:
        leg_config.set_angle(g, "j3", j3)


def half_cycle(stance, swing):
    """stance グループが接地で蹴り、swing グループが空中で振り戻す半サイクル。"""
    j1_push = J1_NEUTRAL + TURN_DIR * SWING        # 蹴り終わり
    j1_recover = J1_NEUTRAL - TURN_DIR * SWING     # 振り出し開始位置

    # 1. swing 脚を持ち上げる
    lift_group(swing, True)
    time.sleep(PHASE_DELAY)
    # 2. swing 脚を前 (振り出し位置) へ、stance 脚を後ろ (蹴り) へ 同時に
    #    同時に動くのは stance 3 + swing 3 だが J1 のみ。J2/J3 は保持。
    smooth_j1(swing, J1_NEUTRAL + TURN_DIR * SWING, j1_recover)
    smooth_j1(stance, j1_recover, j1_push)
    time.sleep(PHASE_DELAY)
    # 3. swing 脚を下ろして接地
    lift_group(swing, False)
    time.sleep(PHASE_DELAY)


legs_str = [leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]
print(f"対象の脚: {legs_str}")
print(f"グループ1: {[leg_config.leg_name(g) for g in GROUP_1]}")
print(f"グループ2: {[leg_config.leg_name(g) for g in GROUP_2]}")
print(f"旋回方向: {'+ (TURN_DIR=+1)' if TURN_DIR > 0 else '- (TURN_DIR=-1)'}")
print(f"立ち姿勢: J2={J2_STAND}, J3={J3_STAND} / J1中立={J1_NEUTRAL}, SWING=±{SWING}")
print("\n前提: 既に立ち姿勢で接地していること (efficient_stand_up.py で先に立たせる)")

try:
    # 立ち姿勢を確実にしておく (J2/J3 を立位に、J1 を中立に)
    print("[準備] 立ち姿勢を保持し J1 を中立へ")
    set_stand(GROUP_1 + GROUP_2)
    time.sleep(0.3)
    set_j1(GROUP_1 + GROUP_2, J1_NEUTRAL)
    time.sleep(0.5)

    for i in range(CYCLES):
        print(f"[サイクル {i+1}/{CYCLES}] G1接地で蹴り / G2空中で戻し")
        half_cycle(GROUP_1, GROUP_2)
        print(f"           G2接地で蹴り / G1空中で戻し")
        half_cycle(GROUP_2, GROUP_1)

    print("\n[終了] J1 を中立に戻す")
    set_j1(GROUP_1 + GROUP_2, J1_NEUTRAL)
    time.sleep(0.5)

except KeyboardInterrupt:
    print("\n中断 - J1 を中立に戻します")
    set_j1(GROUP_1 + GROUP_2, J1_NEUTRAL)

leg_config.deinit()
print("完了")
