"""1脚3軸 (J1 + J2 + J3) の歩行動作のみを繰り返すテストスクリプト。

triple_leg_test.py の step_motion 部分のみを抜き出したもの。
歩行サイクルの調整やデモ用途に使う。
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

# 歩行サイクルの振幅 (中立からのオフセット量, 単位: 度)
LIFT_J3 = 30   # 足を持ち上げる量
LIFT_J2 = 20
SWING = 30     # J1: 脚を前後に振る量
PUSH = 30      # J1: 地面を蹴る量 (= SWING と同じにすると対称)

# 各動作の保持時間 (秒)
T_LIFT = 0.3
T_SWING = 0.3
T_LOWER = 0.3
T_PUSH = 0.4
T_RECOVER = 0.3

# 繰り返し回数
CYCLES = 10


def rest_position():
    print("休眠姿勢へ")
    j3.angle = J3_NEUTRAL
    time.sleep(0.3)
    j2.angle = J2_NEUTRAL
    time.sleep(0.3)
    j1.angle = J1_NEUTRAL
    time.sleep(0.3)


def step(i, total):
    print(f"  ステップ {i+1}/{total}")
    # 1. 足を持ち上げる
    j3.angle = J3_NEUTRAL - LIFT_J3
    j2.angle = J2_NEUTRAL - LIFT_J2
    time.sleep(T_LIFT)
    # 2. 脚を前に振り出す
    j1.angle = J1_NEUTRAL - SWING
    time.sleep(T_SWING)
    # 3. 足を下ろす
    j3.angle = J3_NEUTRAL
    j2.angle = J2_NEUTRAL
    time.sleep(T_LOWER)
    # 4. 脚を後ろに引く (地面を蹴る)
    j1.angle = J1_NEUTRAL + PUSH
    time.sleep(T_PUSH)
    # 5. J1 を中立に戻す
    j1.angle = J1_NEUTRAL
    time.sleep(T_RECOVER)


if __name__ == "__main__":
    print(f"=== 歩行動作テスト ({CYCLES}サイクル) ===")
    print("中断するには Ctrl+C")

    rest_position()
    time.sleep(1)

    try:
        for i in range(CYCLES):
            step(i, CYCLES)
    except KeyboardInterrupt:
        print("\n中断しました")

    print("\n休眠姿勢に戻す")
    rest_position()

    pca.deinit()
    print("完了")
