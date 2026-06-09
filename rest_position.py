"""接続されている全脚を休眠姿勢 (足がまっすぐ伸びた状態) に移動するスクリプト。

組み立て後の動作確認や、何か実行する前の初期姿勢として使う。

  J1 (180度) -> 90度  (中央)
  J2 (180度) -> 90度  (中央)
  J3 (270度) -> 135度 (物理中央)
"""
import time

import leg_config

print(f"対象の脚: {[leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]}")
print("休眠姿勢 (足まっすぐ) に移動します")

# 先端 (J3) から順に動かして、機構の干渉を避ける
print("J3 -> 135度 (オフセット適用済み)")
for group_id in leg_config.CONNECTED_LEGS:
    leg_config.set_angle(group_id, "j3", 135)
    time.sleep(0.2)

print("J2 -> 90度 (オフセット適用済み)")
for group_id in leg_config.CONNECTED_LEGS:
    leg_config.set_angle(group_id, "j2", 90)
    time.sleep(0.2)

print("J1 -> 90度 (オフセット適用済み)")
for group_id in leg_config.CONNECTED_LEGS:
    leg_config.set_angle(group_id, "j1", 90)
    time.sleep(0.2)

input("\n休眠姿勢になりました。Enterで終了")

leg_config.deinit()
print("完了")
