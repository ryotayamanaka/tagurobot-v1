"""1脚3軸 (J1 + J2 + J3) の統合動作テストスクリプト。

組み立て後の足がまっすぐ伸びた状態を中立とする。
各関節の可動範囲は機構の干渉等に応じて調整すること。
"""
import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

# J1: ch12, 180度サーボ (水平回転 / 脚の前後振り)
j1 = servo.Servo(pca.channels[12], min_pulse=500, max_pulse=2500, actuation_range=180)
# J3: ch0, 270度サーボ (上下 / 足先の上げ下げ)
j3 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500, actuation_range=270)
# J2: ch6, 180度サーボ (前後 / 中間関節)
j2 = servo.Servo(pca.channels[6], min_pulse=500, max_pulse=2500, actuation_range=180)

# 動作時の中立角度 (組み立て後、足がまっすぐ伸びた状態)
J1_NEUTRAL = 90    # 180度サーボの物理中央
J2_NEUTRAL = 90    # 180度サーボの物理中央
J3_NEUTRAL = 135   # 270度サーボの物理中央

# 可動範囲 (中立 ± 値)
J1_RANGE = 50  # 40度 〜 140度
J2_RANGE = 60  # 30度 〜 150度
J3_RANGE = 90  # 45度 〜 225度


def rest_position():
    """休眠姿勢 (足がまっすぐ伸びた状態)"""
    print("休眠姿勢へ")
    j3.angle = J3_NEUTRAL
    time.sleep(0.3)
    j2.angle = J2_NEUTRAL
    time.sleep(0.3)
    j1.angle = J1_NEUTRAL
    time.sleep(0.3)


def sweep(target, neutral, rng, step=5):
    """指定サーボを (neutral) → (neutral+rng) → (neutral-rng) → (neutral) でスイープ"""
    hi = neutral + rng
    lo = neutral - rng
    print(f"  {neutral}度 → {hi}度 → {lo}度 → {neutral}度")
    for angle in range(neutral, hi + 1, step):
        target.angle = angle
        time.sleep(0.1)
    for angle in range(hi, lo - 1, -step):
        target.angle = angle
        time.sleep(0.1)
    for angle in range(lo, neutral + 1, step):
        target.angle = angle
        time.sleep(0.1)


def sweep_j1():
    print("J1 スイープ (水平回転)")
    sweep(j1, J1_NEUTRAL, J1_RANGE, step=5)


def sweep_j2():
    print("J2 スイープ (中間関節)")
    sweep(j2, J2_NEUTRAL, J2_RANGE, step=5)


def sweep_j3():
    print("J3 スイープ (先端関節)")
    sweep(j3, J3_NEUTRAL, J3_RANGE, step=10)


def step_motion(cycles=3):
    """歩行動作の模擬: 足を上げる → 前に振り出す → 下ろす → 後ろに引く"""
    print(f"歩行動作シミュレーション ({cycles}回)")
    for i in range(cycles):
        print(f"  ステップ {i+1}/{cycles}")
        # 1. 足を持ち上げる (J3, J2を曲げる)
        j3.angle = J3_NEUTRAL - 30
        j2.angle = J2_NEUTRAL - 20
        time.sleep(0.3)
        # 2. 脚を前に振り出す (J1)
        j1.angle = J1_NEUTRAL - 30
        time.sleep(0.3)
        # 3. 足を下ろす (J3, J2を戻す)
        j3.angle = J3_NEUTRAL
        j2.angle = J2_NEUTRAL
        time.sleep(0.3)
        # 4. 脚を後ろに引く (J1) = 地面を蹴る
        j1.angle = J1_NEUTRAL + 30
        time.sleep(0.4)
        # 5. 中立に戻す
        j1.angle = J1_NEUTRAL
        time.sleep(0.3)


if __name__ == "__main__":
    print("=== 1脚 3軸統合動作テスト ===")

    print("\n[1/5] 休眠姿勢")
    rest_position()
    time.sleep(1)

    print("\n[2/5] J1 スイープ")
    sweep_j1()
    time.sleep(1)

    print("\n[3/5] J2 スイープ")
    sweep_j2()
    time.sleep(1)

    print("\n[4/5] J3 スイープ")
    sweep_j3()
    time.sleep(1)

    print("\n[5/5] 歩行動作")
    step_motion(cycles=3)
    time.sleep(1)

    print("\n休眠姿勢に戻す")
    rest_position()

    pca.deinit()
    print("\n完了")
