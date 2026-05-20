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

# 中立角度 (組み立て姿勢: 両サーボとも物理端=180度)
# 180度は物理限界のため、可動範囲は中立から負方向のみ
J2_NEUTRAL = 180
J3_NEUTRAL = 180

# 可動範囲 (中立からの最大変位量)
J2_RANGE = 60  # 120度〜180度
J3_RANGE = 90  # 90度〜180度


def rest_position():
    """休眠姿勢 (組み立て位置)"""
    print("休眠姿勢へ")
    j3.angle = J3_NEUTRAL
    time.sleep(0.3)
    j2.angle = J2_NEUTRAL
    time.sleep(0.3)


def sweep_j2():
    """J2 (中間関節) を可動範囲でスイープ (中立 -> 最遠 -> 中立)"""
    lo = J2_NEUTRAL - J2_RANGE
    print(f"J2 スイープ ({J2_NEUTRAL}° → {lo}° → {J2_NEUTRAL}°)")
    for angle in range(J2_NEUTRAL, lo - 1, -5):
        j2.angle = angle
        time.sleep(0.1)
    for angle in range(lo, J2_NEUTRAL + 1, 5):
        j2.angle = angle
        time.sleep(0.1)


def sweep_j3():
    """J3 (先端関節) を可動範囲でスイープ (中立 -> 最遠 -> 中立)"""
    lo = J3_NEUTRAL - J3_RANGE
    print(f"J3 スイープ ({J3_NEUTRAL}° → {lo}° → {J3_NEUTRAL}°)")
    for angle in range(J3_NEUTRAL, lo - 1, -10):
        j3.angle = angle
        time.sleep(0.1)
    for angle in range(lo, J3_NEUTRAL + 1, 10):
        j3.angle = angle
        time.sleep(0.1)


def step_motion(cycles=3):
    """歩行動作の模擬 (足を上げて前に出して下ろす)
    180度中立では負方向のみ動けるため、すべて中立より小さい角度で構成する。
    """
    print(f"歩行動作シミュレーション ({cycles}回)")
    for i in range(cycles):
        print(f"  ステップ {i+1}/{cycles}")
        # 足を持ち上げる (J3を中立から大きく曲げる)
        j3.angle = J3_NEUTRAL - 60
        time.sleep(0.3)
        # 前に出す (J2を中立から曲げる)
        j2.angle = J2_NEUTRAL - 40
        time.sleep(0.3)
        # 足を下ろす (J3を中立寄りに戻す)
        j3.angle = J3_NEUTRAL - 20
        time.sleep(0.3)
        # 後ろに引く (J2を中立寄りに戻す = 地面を蹴る)
        j2.angle = J2_NEUTRAL - 10
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
