import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

# J3: ch0, 270度サーボ
j3 = servo.Servo(pca.channels[0], min_pulse=500, max_pulse=2500, actuation_range=270)
# J2: ch6, 180度サーボ
j2 = servo.Servo(pca.channels[6], min_pulse=500, max_pulse=2500, actuation_range=180)

# main.py のオフセット値に対応する中立角度
J2_NEUTRAL = 140  # 180度サーボ
J3_NEUTRAL = 150  # 270度サーボ


def rest_position():
    """休眠姿勢 (main.py: rest_position相当)"""
    print("休眠姿勢へ")
    j3.angle = J3_NEUTRAL
    time.sleep(0.3)
    j2.angle = J2_NEUTRAL
    time.sleep(0.3)


def standing_position():
    """立ち上がる動き (main.py: standing_position相当)"""
    print("立ち上がる")
    for angle in range(J2_NEUTRAL, 89, -10):
        j2.angle = angle
        time.sleep(0.15)
    j3.angle = J3_NEUTRAL + 40
    time.sleep(0.3)


def sweep_j2():
    """J2 (中間関節) を可動範囲でスイープ"""
    print("J2 スイープ (110° → 170° → 140°)")
    for angle in range(J2_NEUTRAL, 170, 5):
        j2.angle = angle
        time.sleep(0.1)
    for angle in range(170, 109, -5):
        j2.angle = angle
        time.sleep(0.1)
    for angle in range(110, J2_NEUTRAL + 1, 5):
        j2.angle = angle
        time.sleep(0.1)


def sweep_j3():
    """J3 (先端関節) を可動範囲でスイープ"""
    print("J3 スイープ (60° → 240° → 150°)")
    for angle in range(J3_NEUTRAL, 240, 10):
        j3.angle = angle
        time.sleep(0.1)
    for angle in range(240, 59, -10):
        j3.angle = angle
        time.sleep(0.1)
    for angle in range(60, J3_NEUTRAL + 1, 10):
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
