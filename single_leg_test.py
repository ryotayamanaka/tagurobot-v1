import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

# J3: ch0, 180度サーボ (本来は270度サーボ想定だが180度で代用)
j3 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500, actuation_range=180)
# J2: ch6, 180度サーボ
j2 = servo.Servo(pca.channels[6], min_pulse=500, max_pulse=2500, actuation_range=180)

# 動作時の中立角度 (組み立て後、足がまっすぐ伸びた状態)
# 組み立て時はホーンを J2=0度 / J3=180度 で取り付けるが、組み立て後の
# 動作テストは 90度 中立 (両方向に対称に動かせる) を基準にする
J2_NEUTRAL = 90
J3_NEUTRAL = 90

# 可動範囲 (中立 ± 値)
J2_RANGE = 60  # 30度〜150度
J3_RANGE = 90  # 0度〜180度 (フル範囲)


def rest_position():
    """休眠姿勢 (足がまっすぐ伸びた状態)"""
    print("休眠姿勢へ")
    j3.angle = J3_NEUTRAL
    time.sleep(0.3)
    j2.angle = J2_NEUTRAL
    time.sleep(0.3)


def sweep_j2():
    """J2 (中間関節) を可動範囲でスイープ"""
    lo = J2_NEUTRAL - J2_RANGE
    hi = J2_NEUTRAL + J2_RANGE
    print(f"J2 スイープ ({lo}° → {hi}° → {J2_NEUTRAL}°)")
    for angle in range(J2_NEUTRAL, hi + 1, 5):
        j2.angle = angle
        time.sleep(0.1)
    for angle in range(hi, lo - 1, -5):
        j2.angle = angle
        time.sleep(0.1)
    for angle in range(lo, J2_NEUTRAL + 1, 5):
        j2.angle = angle
        time.sleep(0.1)


def sweep_j3():
    """J3 (先端関節) を可動範囲でスイープ"""
    lo = J3_NEUTRAL - J3_RANGE
    hi = J3_NEUTRAL + J3_RANGE
    print(f"J3 スイープ ({lo}° → {hi}° → {J3_NEUTRAL}°)")
    for angle in range(J3_NEUTRAL, hi + 1, 10):
        j3.angle = angle
        time.sleep(0.1)
    for angle in range(hi, lo - 1, -10):
        j3.angle = angle
        time.sleep(0.1)
    for angle in range(lo, J3_NEUTRAL + 1, 10):
        j3.angle = angle
        time.sleep(0.1)


def step_motion(cycles=3):
    """歩行動作の模擬 (足を上げて前に出して下ろす)"""
    print(f"歩行動作シミュレーション ({cycles}回)")
    for i in range(cycles):
        print(f"  ステップ {i+1}/{cycles}")
        # 足を持ち上げる (J3を曲げる)
        j3.angle = J3_NEUTRAL - 30
        time.sleep(0.3)
        # 前に出す (J2を前方へ)
        j2.angle = J2_NEUTRAL - 20
        time.sleep(0.3)
        # 足を下ろす (J3を伸ばす)
        j3.angle = J3_NEUTRAL + 20
        time.sleep(0.3)
        # 後ろに引く (J2を後方へ = 地面を蹴る)
        j2.angle = J2_NEUTRAL + 20
        time.sleep(0.3)
        # 中立に戻す
        j3.angle = J3_NEUTRAL
        j2.angle = J2_NEUTRAL
        time.sleep(0.3)


if __name__ == '__main__':
    print("=== 1脚 2軸動作テスト ===")

    print("\n[1/4] 休眠姿勢")
    rest_position()
    time.sleep(1)

    print("\n[2/4] J2 スイープ")
    sweep_j2()
    time.sleep(1)

    print("\n[3/4] J3 スイープ")
    sweep_j3()
    time.sleep(1)

    print("\n[4/4] 歩行動作")
    step_motion(cycles=3)
    time.sleep(1)

    print("\n休眠姿勢に戻す")
    rest_position()

    pca.deinit()
    print("\n完了")
