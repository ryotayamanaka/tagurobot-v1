"""対話的にサーボを動かすスクリプト (複数脚対応)。

脚と関節を指定して角度を入力するとサーボを動かす。

使い方:
  $ python3 interactive_servo.py
  > a j1 90      # 脚A の J1 を 90度に
  > c j3 135     # 脚C の J3 を 135度に
  > a j2 30      # 脚A の J2 を 30度に
  > status       # 現在の指示角度を表示
  > q            # 終了
"""
import leg_config

# 関節の可動範囲 (leg_config に集約)
JOINT_TYPES = leg_config.JOINT_RANGE

# 脚名 (a/b/c/...) と group_id の対応
LEG_NAMES = {leg_config.leg_name(g).lower(): g for g in leg_config.CONNECTED_LEGS}

# 指示済み論理角度のキャッシュ (status 表示用)
current = {}  # key: (leg_name, joint_name)


def print_help():
    print("コマンド:")
    print("  <脚> <関節> <角度>   サーボを指定角度に動かす (例: a j1 90)")
    print("  status               現在の指示角度を表示")
    print("  help                 このヘルプを表示")
    print("  q / quit             終了")
    print("脚:")
    for name, gid in LEG_NAMES.items():
        print(f"  {name}: 脚{leg_config.leg_name(gid)}")
    print("関節:")
    print("  j1: 根元 (180度サーボ)")
    print("  j2: 中間 (180度サーボ)")
    print("  j3: 先端 (270度サーボ)")


def print_status():
    if not current:
        print("まだ角度指示なし")
        return
    print("現在の指示角度:")
    for (leg_name_lower, joint_name), val in sorted(current.items()):
        print(f"  脚{leg_name_lower.upper()} {joint_name}: {val}度")


print("=== 対話的サーボ制御 (複数脚対応) ===")
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
        if len(parts) != 3:
            print("形式: <脚> <関節> <角度> (例: a j1 90)")
            continue

        leg_name_lower, joint_name, angle_str = parts

        if leg_name_lower not in LEG_NAMES:
            print(f"不明な脚: {leg_name_lower}. 使えるのは {list(LEG_NAMES.keys())}")
            continue
        if joint_name not in JOINT_TYPES:
            print(f"不明な関節: {joint_name}. 使えるのは {list(JOINT_TYPES.keys())}")
            continue

        try:
            angle = float(angle_str)
        except ValueError:
            print(f"角度は数値で指定: {angle_str}")
            continue

        rng = JOINT_TYPES[joint_name]
        if angle < 0 or angle > rng:
            print(f"範囲外: {joint_name} は 0-{rng}度のみ")
            continue

        group_id = LEG_NAMES[leg_name_lower]
        try:
            actual_angle = leg_config.set_angle(group_id, joint_name, angle)
            current[(leg_name_lower, joint_name)] = angle
            print(f"脚{leg_name_lower.upper()} {joint_name} -> {angle}度 (実際: {actual_angle}度)")
        except Exception as e:
            print(f"エラー: {e}")

except KeyboardInterrupt:
    print("\n中断しました")

leg_config.deinit()
print("完了")
