"""サーボの可動範囲が180度か270度かを確認するスクリプト。

actuation_range=270 で初期化し、0度から段階的に角度を上げて、
どこで物理限界に達するかを目視で確認する。

物理限界に達するとサーボは指示通り動けず、ガガガと唸り続けるため、
異音がしたらEnterを押す前に Ctrl+C で中断すること。
"""
import time
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

CHANNEL = 1  # 確認するチャネル

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

# 270度で初期化 (180度サーボでも、180度を超える指示は受け付けるが物理的に動けない)
target = servo.Servo(
    pca.channels[CHANNEL],
    min_pulse=500,
    max_pulse=2500,
    actuation_range=270,
)

# 段階的に動かす角度のリスト
steps = [0, 45, 90, 135, 180, 200, 220, 240, 270]

print(f"=== ch{CHANNEL} のサーボ可動範囲確認 ===")
print("各角度に移動するので、ホーンの動きと異音を観察してください")
print("異音(ガガガ)が出たら、その手前の角度が物理限界です")
print("中断する場合は Ctrl+C")
print()

try:
    for angle in steps:
        print(f"  -> {angle}度")
        target.angle = angle
        time.sleep(2)
        input(f"    {angle}度: 動きましたか？ Enterで次へ (異音があれば Ctrl+C)")
except KeyboardInterrupt:
    print("\n中断しました")

print("\n中央(90度)に戻します")
target.angle = 90
time.sleep(1)

pca.deinit()
print("完了")
