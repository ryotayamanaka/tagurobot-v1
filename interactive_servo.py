"""対話的にサーボを動かすスクリプト。

関節を選択 (j1/j2/j3) して角度を入力するとサーボを動かす。
可動範囲の境界を探したり、組み立て後の調整に使う。

使い方:
  $ python3 interactive_servo.py
  > j1 90      # J1 を 90度に
  > j2 30      # J2 を 30度に
  > j3 180     # J3 を 180度に
  > status     # 現在の角度を表示
  > q          # 終了
"""
import busio
from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from board import SCL, SDA

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50

# 関節定義: (チャネル, 可動範囲, 表示名)
JOINTS = {
    "j1": (12, 180, "J1 (ch12, 180度)"),
    "j2": (6, 180, "J2 (ch6, 180度)"),
    "j3": (0, 270, "J3 (ch0, 270度)"),
}

servos = {}
for name, (ch, rng, _label) in JOINTS.items():
    servos[name] = servo.Servo(
        pca.channels[ch],
        min_pulse=500,
        max_pulse=2500,
        actuation_range=rng,
    )

current = {name: None for name in JOINTS}


def print_help():
    print("コマンド:")
    print("  <関節> <角度>   サーボを指定角度に動かす (例: j1 90)")
    print("  status          現在の指示角度を表示")
    print("  help            このヘルプを表示")
    print("  q / quit        終了")
    print("関節:")
    for name, (_ch, rng, label) in JOINTS.items():
        print(f"  {name}: {label}, 範囲 0-{rng}度")


def print_status():
    print("現在の指示角度:")
    for name, (_ch, _rng, label) in JOINTS.items():
        val = current[name]
        val_str = f"{val}度" if val is not None else "未設定"
        print(f"  {name} ({label}): {val_str}")


print("=== 対話的サーボ制御 ===")
print_help()

try:
    while True:
        try:
            line = input("\n> ").strip().lower()
        except EOFError:
            break
        if not line:
            continue
        if line in ("q", "quit", "exit"):
            break
        if line == "help":
            print_help()
            continue
        if line == "status":
            print_status()
            continue

        parts = line.split()
        if len(parts) != 2:
            print("形式: <関節> <角度> (例: j1 90)")
            continue

        name, angle_str = parts
        if name not in JOINTS:
            print(f"不明な関節: {name}. 使えるのは {list(JOINTS.keys())}")
            continue

        try:
            angle = float(angle_str)
        except ValueError:
            print(f"角度は数値で指定: {angle_str}")
            continue

        _ch, rng, label = JOINTS[name]
        if angle < 0 or angle > rng:
            print(f"範囲外: {label} は 0-{rng}度のみ")
            continue

        try:
            servos[name].angle = angle
            current[name] = angle
            print(f"{label} -> {angle}度")
        except Exception as e:
            print(f"エラー: {e}")

except KeyboardInterrupt:
    print("\n中断しました")

pca.deinit()
print("完了")
