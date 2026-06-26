"""6脚 直進歩行 (オリジナル main.py の歩行軌道を gait.py 経由で実行)。

gait.py が座標ベースの足先軌道・逆運動学・サーボ角変換を担う。本スクリプトは
時刻 cnt を進めながら全脚の (j1,j2,j3) を leg_config に出すだけ。

放射状配置 (上から見て時計回り A〜F) で、全脚を同じ進行方向へ向けて足先を
前後させることで直進する。偶奇脚の位相差 (π/2, π) で交互歩容になる。

前提: 既に概ね立っていること。歩行は gait の定める立ち高さ (J3≈220-254,
J2≈126-142) で行うため、開始時にまずその歩行初期姿勢へ滑らかに移行してから
歩き出す。

調整: 速度は STEP_DELAY、歩幅は gait.STROKE_LENGTH_A、足上げ高さは
gait.STROKE_LENGTH_B で変える。電力が厳しければ STEP_DELAY を増やし
(ゆっくり)、歩幅・足上げを小さくする。まずは「その場足踏み」(歩幅小) で
安全確認してから歩幅を上げるのが安全。
"""
import time

import leg_config
import gait

# 1 サイクル(=NUM_DIVIDE 分割)を何周するか
CYCLES = 3
# 各 cnt 間の待ち時間 (大きいほどゆっくり = 低電力)
STEP_DELAY = 0.03
# 歩行初期姿勢へ移行するときの 1 度あたり待ち時間
MOVE_DELAY = 0.02


def apply(leg, j1, j2, j3):
    leg_config.set_angle(leg, "j1", j1)
    leg_config.set_angle(leg, "j2", j2)
    leg_config.set_angle(leg, "j3", j3)


def goto_walk_start():
    """全脚を歩行初期姿勢 (cnt=0 の角度) へ滑らかに移行する。

    現在の角度が不明なので、各脚の現在指令値を持たず、中立 (90/135/135) から
    歩行初期姿勢へ線形補間する。立ち姿勢からの呼び出しを想定。
    """
    print("[準備] 歩行初期姿勢へ移行")
    targets = {leg: gait.servo_angles(leg, 0) for leg in leg_config.CONNECTED_LEGS}
    start = {leg: (gait.J1_NEUTRAL, gait.J2_NEUTRAL, gait.J3_NEUTRAL)
             for leg in leg_config.CONNECTED_LEGS}
    steps = 30
    for s in range(steps + 1):
        t = s / steps
        for leg in leg_config.CONNECTED_LEGS:
            j1 = start[leg][0] + (targets[leg][0] - start[leg][0]) * t
            j2 = start[leg][1] + (targets[leg][1] - start[leg][1]) * t
            j3 = start[leg][2] + (targets[leg][2] - start[leg][2]) * t
            apply(leg, j1, j2, j3)
        time.sleep(MOVE_DELAY)


legs_str = [leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]
print(f"対象の脚: {legs_str}")
print(f"歩幅={gait.STROKE_LENGTH_A}m 足上げ={gait.STROKE_LENGTH_B}m "
      f"分割={gait.NUM_DIVIDE} サイクル={CYCLES} STEP_DELAY={STEP_DELAY}")
print("前提: 概ね立っていること (Ctrl+C で中断)")

try:
    goto_walk_start()
    time.sleep(0.3)

    print("[歩行] 開始")
    for c in range(CYCLES):
        print(f"  サイクル {c+1}/{CYCLES}")
        for cnt in range(gait.NUM_DIVIDE):
            for leg in leg_config.CONNECTED_LEGS:
                j1, j2, j3 = gait.servo_angles(leg, cnt)
                apply(leg, j1, j2, j3)
            time.sleep(STEP_DELAY)

    print("[終了] 歩行初期姿勢で停止")

except KeyboardInterrupt:
    print("\n中断しました")

leg_config.deinit()
print("完了")
