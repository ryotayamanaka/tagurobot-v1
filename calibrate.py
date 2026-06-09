"""サーボのオフセット (取り付け誤差の補正値) を測定して保存するスクリプト。

サーボを基準姿勢 (rest状態: J1=90, J2=90, J3=135) に動かして、
ホーンが理想の向きと一致するまで u/d で微調整する。

保存先: calibration.json (.gitignore で除外、機体個別の設定)
形式:
  {
    "0": {"j1": 3, "j2": -2, "j3": 1},
    "2": {...},
    ...
  }
key は group_id (文字列)、値はオフセット (度、整数)。

使い方:
  $ python3 calibrate.py
  脚を選択: a
  関節を選択: j1
  ...微調整...
  s で保存
"""
import json
import os

import leg_config

CALIBRATION_FILE = "calibration.json"

# 基準位置 (rest 状態)
NEUTRAL = {
    "j1": 90,
    "j2": 90,
    "j3": 135,
}

# 関節の一覧 (可動範囲・チャネル・ボードの解決は leg_config に集約)
JOINT_TYPES = leg_config.JOINT_RANGE


def load_calibration():
    if not os.path.exists(CALIBRATION_FILE):
        return {}
    with open(CALIBRATION_FILE) as f:
        return json.load(f)


def save_calibration(data):
    with open(CALIBRATION_FILE, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)


def main():
    try:
        # 脚を選択
        leg_options = {leg_config.leg_name(g).lower(): g for g in leg_config.CONNECTED_LEGS}
        print(f"接続されている脚: {list(leg_options.keys())}")
        leg_input = input("脚を選択 (例: a): ").strip().lower()
        if leg_input not in leg_options:
            print(f"不明な脚: {leg_input}")
            return
        group_id = leg_options[leg_input]
        leg = leg_config.leg_name(group_id)

        # 関節を選択
        print(f"関節: {list(JOINT_TYPES.keys())}")
        joint = input("関節を選択 (例: j1): ").strip().lower()
        if joint not in JOINT_TYPES:
            print(f"不明な関節: {joint}")
            return

        rng = JOINT_TYPES[joint]
        neutral = NEUTRAL[joint]

        # 既存のオフセットを読み込む
        cal = load_calibration()
        offset = cal.get(str(group_id), {}).get(joint, 0)

        # サーボを準備 (ボード・チャネルの解決は leg_config が行う)
        target = leg_config.get_servo(group_id, joint)

        def apply():
            # キャリブレーションは生の (基準 + オフセット) を直接指示する。
            # apply_offset は使わない (二重適用になるため)。
            angle = neutral + offset
            if angle < 0 or angle > rng:
                print(f"  警告: 指示角度 {angle} が可動範囲 (0-{rng}) を超えています")
                return
            target.angle = angle
            print(f"  脚{leg} {joint}: 基準 {neutral} + オフセット {offset:+d} = {angle}度")

        print(f"\n脚{leg} {joint} を基準位置 {neutral} 度に動かします")
        apply()

        print("\nコマンド:")
        print("  u : +1 度")
        print("  d : -1 度")
        print("  r : オフセットをリセット (0 に戻す)")
        print("  s : 保存して終了")
        print("  q : 保存せずに終了")

        while True:
            cmd = input("> ").strip().lower()
            if cmd == "u":
                offset += 1
                apply()
            elif cmd == "d":
                offset -= 1
                apply()
            elif cmd == "r":
                offset = 0
                apply()
            elif cmd == "s":
                cal.setdefault(str(group_id), {})[joint] = offset
                save_calibration(cal)
                print(f"保存しました: 脚{leg} {joint} オフセット = {offset:+d}度")
                break
            elif cmd == "q":
                print("保存せずに終了")
                break
            else:
                print("不明なコマンド (u/d/r/s/q)")

    finally:
        leg_config.deinit()


if __name__ == "__main__":
    main()
