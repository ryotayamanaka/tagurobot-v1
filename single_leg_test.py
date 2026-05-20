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

# 中立角度 (組み立て姿勢)
# J2 は 0度、J3 は 180度 で arm.stl に取り付ける構造
# サーボは中立から物理限界(0/180)を超えない方向にのみ動かせる
J2_NEUTRAL = 0
J3_NEUTRAL = 180

# 可動範囲 (中立から動かせる方向の最大変位量)
# J2: 中立 0度 → 正方向のみ
# J3: 中立 180度 → 負方向のみ
J2_RANGE = 60   # 0度 〜 60度
J3_RANGE = 90   # 90度 〜 180度

# 各サーボの動かせる方向 (+1: 中立から正方向, -1: 中立から負方向)
J2_DIR = +1
J3_DIR = -1


def _j2_angle(offset):
    """中立からのオフセット(正の値)を実際の角度に変換"""
    return J2_NEUTRAL + J2_DIR * offset


def _j3_angle(offset):
    """中立からのオフセット(正の値)を実際の角度に変換"""
    return J3_NEUTRAL + J3_DIR * offset


def rest_position():
    """休眠姿勢 (組み立て位置)"""
    print("休眠姿勢へ")
    j3.angle = J3_NEUTRAL
    time.sleep(0.3)
    j2.angle = J2_NEUTRAL
    time.sleep(0.3)


def sweep_j2():
    """J2 (中間関節) を可動範囲でスイープ"""
    print(f"J2 スイープ ({J2_NEUTRAL}° → {_j2_angle(J2_RANGE)}° → {J2_NEUTRAL}°)")
    for offset in range(0, J2_RANGE + 1, 5):
        j2.angle = _j2_angle(offset)
        time.sleep(0.1)
    for offset in range(J2_RANGE, -1, -5):
        j2.angle = _j2_angle(offset)
        time.sleep(0.1)


def sweep_j3():
    """J3 (先端関節) を可動範囲でスイープ"""
    print(f"J3 スイープ ({J3_NEUTRAL}° → {_j3_angle(J3_RANGE)}° → {J3_NEUTRAL}°)")
    for offset in range(0, J3_RANGE + 1, 10):
        j3.angle = _j3_angle(offset)
        time.sleep(0.1)
    for offset in range(J3_RANGE, -1, -10):
        j3.angle = _j3_angle(offset)
        time.sleep(0.1)


def step_motion(cycles=3):
    """歩行動作の模擬 (足を上げて前に出して下ろす)"""
    print(f"歩行動作シミュレーション ({cycles}回)")
    for i in range(cycles):
        print(f"  ステップ {i+1}/{cycles}")
        # 足を持ち上げる (J3を中立から大きく動かす)
        j3.angle = _j3_angle(60)
        time.sleep(0.3)
        # 前に出す (J2を中立から動かす)
        j2.angle = _j2_angle(40)
        time.sleep(0.3)
        # 足を下ろす (J3を中立寄りに戻す)
        j3.angle = _j3_angle(20)
        time.sleep(0.3)
        # 後ろに引く (J2を中立寄りに戻す = 地面を蹴る)
        j2.angle = _j2_angle(10)
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
