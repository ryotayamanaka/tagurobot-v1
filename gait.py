"""6脚 直進歩行の運動学 (ハード非依存の純粋計算モジュール)。

オリジナル main.py の Hexapod クラスから、座標ベースの歩行ロジックを抽出した:
  - 足先軌道の生成 (main.py 416-450 行)
  - 逆運動学 calc_backward (main.py 225-254 行)
  - サーボ角への変換 (main.py control 111-131 行)

放射状配置 (上から見て時計回りに A,B,C,D,E,F、脚 i の取り付け方位 = 60°×i)。
全脚を「同じ進行方向」へ向けて足先を前後させることで直進する。脚ごとに
取り付け方位が違うため、theta1 (J1) は方位を加味して計算する。

## 進行方向 (実機で確定 2026-06-26)

このモジュールは抽象座標で「全脚の足先を -y へ蹴り、機体を +y へ進める」と
仮定して書かれている (オリジナル main.py 同様)。しかし実機では座標系と物理の
対応が逆で、実際には **脚 E と F の間の方向へ前進する**。これを「前」と
定めた。バグではなく座標系の向きの取り決めの問題。逆向き (B-C 間) に進めたい
場合は foot_target の `y = y0 - ...` を `y = y0 + ...` に反転する。

## 角度系の橋渡し (重要)

オリジナルは旧 180° サーボ前提で、theta はラジアン (中立 0)、独自オフセット
(J1=90, J2=140, J3=150 度) でサーボ角へ変換していた。本プロジェクトは現在:
  - J2/J3 を 270° サーボ化、中立は物理中央 135°
  - 取り付け誤差は calibration.json (leg_config 側で適用)
そのため、ここでは「中立 135° / 270°」系に合わせた変換を行い、
leg_config.set_angle() に渡せる論理角度 (度) を返す。オフセット
(calibration.json) の適用は leg_config 側に任せる (二重適用を避ける)。

使い方:
    import gait
    for cnt in range(...):
        for leg in range(6):
            j1, j2, j3 = gait.servo_angles(leg, cnt)
            leg_config.set_angle(leg, "j1", j1)
            leg_config.set_angle(leg, "j2", j2)
            leg_config.set_angle(leg, "j3", j3)
"""
import math

# --- 機体諸元 (main.py init_position と同じ, 単位 m) ---
SIDE_LENGTH = 0.1          # 胴体中心から J1 までの距離 (描画用, IK には不使用)
LONG1 = 0.04               # J1-J2 リンク長
LONG2 = 0.08               # J2-J3 リンク長
LONG3 = 0.08               # J3-足先 リンク長

# --- 歩行パラメータ (main.py timer_func と同じ既定値) ---
NUM_DIVIDE = 100           # 1 周期の分割数 (大きいほど小刻み)
STROKE_LENGTH_A = 0.03     # 一歩の歩幅 (m)  ※オリジナル既定値。足踏み(0.01)確認済み
STROKE_LENGTH_B = 0.01     # 一歩の足上げ高さ (m)
DISTANCE_A = 0.1           # TOP VIEW で J1 から足先定位置までの距離 (m)
DISTANCE_B = -0.08         # SIDE VIEW で関節から地面までの距離 (m)

# --- 中立角度 (本プロジェクトの leg_config 流儀) ---
J1_NEUTRAL = 90            # 180° サーボの物理中央
J2_NEUTRAL = 135           # 270° サーボの物理中央
J3_NEUTRAL = 135           # 270° サーボの物理中央

LEG_STEP = 2.0 * math.pi / 6.0   # 脚の取り付け方位刻み (60°)


def _relu(a):
    return a if a > 0 else 0


def foot_target(leg, cnt):
    """時刻 cnt における脚 leg の足先目標 (swing[rad], distance[m], height[m])。

    main.py 433-450 行の軌道生成を 1 脚分に切り出したもの。
    偶数脚と奇数脚で位相を π/2・π ずらして交互歩容を作る。

    swing は「その脚の取り付け方位を基準にした前後の振り量」(中立で 0)。
    main.py は theta1 = atan2(-y,x) を取り付け方位込みで持っていたが、ここでは
    方位分を引いて純粋な振り量を返す (J1 の中立 90° に乗せやすくするため)。
    """
    tmp1 = LEG_STEP                       # 取り付け方位刻み
    tmp2 = 2.0 * math.pi / NUM_DIVIDE     # 時間位相の刻み

    phase_diff1 = math.pi / 2 if (leg % 2 != 0) else 0
    phase_diff2 = math.pi if (leg % 2 != 0) else 0

    # 足先の定位置 (取り付け方位方向に DISTANCE_A 離れた点)
    x0 = DISTANCE_A * math.cos(tmp1 * leg)
    y0 = DISTANCE_A * math.sin(tmp1 * leg)
    # 進行方向 (y) に歩幅分だけ前後させる
    y = y0 - STROKE_LENGTH_A * math.fabs(math.sin(tmp2 * cnt + phase_diff1))

    # 振り量 = 現在の足先方位 − 定位置方位。±π に正規化 (脚3 の方位 180° で
    # atan2 が境界をまたぐのを防ぐ)。
    swing = math.atan2(-y, x0) - math.atan2(-y0, x0)
    swing = (swing + math.pi) % (2 * math.pi) - math.pi

    distance = math.sqrt(x0 * x0 + y * y)
    height = DISTANCE_B + math.fabs(
        _relu(STROKE_LENGTH_B * math.sin(tmp2 * 2 * cnt + phase_diff2)))
    return swing, distance, height


def inverse_kinematics(distance, height):
    """足先座標 (distance, height) から (theta2, theta3) [rad] を解く。

    main.py calc_backward (225-254 行) の余弦定理。解が無い (届かない座標)
    場合は None を返す。
    """
    real_x = distance - LONG1
    real_y = height
    L = math.sqrt(real_x * real_x + real_y * real_y)
    try:
        J3 = math.acos((LONG2 * LONG2 + LONG3 * LONG3 - L * L) / (2 * LONG2 * LONG3))
        B = math.acos((L * L + LONG2 * LONG2 - LONG3 * LONG3) / (2 * L * LONG2))
        A = math.fabs(math.atan(real_y / real_x))
        theta2 = B - A
        theta3 = -(math.pi - J3)
        return theta2, theta3
    except (ValueError, ZeroDivisionError):
        return None


def servo_angles(leg, cnt):
    """脚 leg・時刻 cnt の論理サーボ角 (j1, j2, j3) [度] を返す。

    leg_config.set_angle() にそのまま渡せる (オフセット未適用の論理角度)。
    解が無い場合は中立角度を返す (安全側)。

    角度系の橋渡し:
      theta1: 取り付け方位を引いて中立 J1_NEUTRAL を中心に。後 3 脚 (D,E,F)
              は方位が反対側を向くため向きを反転 (main.py control 126-131 行)。
      theta2/theta3: ラジアン→度に変換し、中立 135° を中心に乗せる。
    """
    swing, distance, height = foot_target(leg, cnt)
    ik = inverse_kinematics(distance, height)
    if ik is None:
        return J1_NEUTRAL, J2_NEUTRAL, J3_NEUTRAL
    theta2, theta3 = ik

    # swing は方位を基準にした純粋な前後振り量 (中立 0)。中立 90° に乗せる。
    # 後 3 脚 (D,E,F) は放射状で胴体の反対側を向くため J1 の向きを反転。
    if leg >= 3:
        j1 = J1_NEUTRAL - math.degrees(swing)
    else:
        j1 = J1_NEUTRAL + math.degrees(swing)

    # J2/J3: ラジアンの相対角を度にし、中立 135° を中心に乗せる。
    # オリジナルは control で +offset / -theta3 としていた符号関係を踏襲する。
    j2 = J2_NEUTRAL + math.degrees(theta2)
    j3 = J3_NEUTRAL - math.degrees(theta3)

    return j1, j2, j3
