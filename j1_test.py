"""J1 (ch1, 180度サーボ) を安全な可動範囲でテストするスクリプト。

中立 90度から ±60度 (30度 〜 150度) の範囲で動かす。
範囲を広げる場合は、機構が物理的に動ける範囲を確認してから定数を変更すること。
"""
import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

CHANNEL = 1

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
# 機構の干渉等を確認しながら、必要に応じて狭める
J1_RANGE = 60  # 30度 〜 150度


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
