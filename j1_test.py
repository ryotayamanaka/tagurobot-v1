"""J1 (ch12, 180度サーボ) を安全な可動範囲でテストするスクリプト。

中立 90度から ±30度 (60度 〜 120度) の範囲で動かす。
機構の干渉を実測で確認した範囲。
"""
import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

CHANNEL = 12

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

j1 = servo.Servo(
    pca.channels[CHANNEL],
    min_pulse=500,
    max_pulse=2500,
    actuation_range=180,
)

# 動作時の中立角度 (180度サーボの物理中央)
J1_NEUTRAL = 90

# 可動範囲 (中立 ± 値)
# 実測の機構干渉限界
J1_RANGE = 30  # 60度 〜 120度


def rest_position():
    print(f"中立 ({J1_NEUTRAL}度) へ")
    j1.angle = J1_NEUTRAL
    time.sleep(0.5)


def sweep_j1():
    lo = J1_NEUTRAL - J1_RANGE
    hi = J1_NEUTRAL + J1_RANGE
    print(f"J1 スイープ ({lo}度 → {hi}度 → {J1_NEUTRAL}度)")
    for angle in range(J1_NEUTRAL, hi + 1, 5):
        j1.angle = angle
        time.sleep(0.1)
    for angle in range(hi, lo - 1, -5):
        j1.angle = angle
        time.sleep(0.1)
    for angle in range(lo, J1_NEUTRAL + 1, 5):
        j1.angle = angle
        time.sleep(0.1)


if __name__ == "__main__":
    print("=== J1 動作テスト ===")
    rest_position()
    time.sleep(1)
    sweep_j1()
    time.sleep(1)
    rest_position()

    pca.deinit()
    print("完了")
