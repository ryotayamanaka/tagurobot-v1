"""接続されている全脚を収納姿勢に折りたたむスクリプト。

しまう時にコンパクトな姿勢にする。

  J1 (180度) -> 90度  (中央)
  J2 (270度) -> 220度 (折りたたみ: 中立135+85。実機で一番きれいに収まった値)
  J3 (270度) -> 40度  (実機で一番きれいに収まった値)
"""
import time

import leg_config

print(f"対象の脚: {[leg_config.leg_name(g) for g in leg_config.CONNECTED_LEGS]}")
print("収納姿勢に折りたたみます")

# まず J1 を中央に戻して脚の向きを揃える
print("J1 (180度) -> 90度 (中央, オフセット適用済み)")
for group_id in leg_config.CONNECTED_LEGS:
    leg_config.set_angle(group_id, "j1", 90)
    time.sleep(0.3)

# 次に J2 を 220度に (中立135 + 85。実機で一番きれいに収まった値)
print("J2 (270度) -> 220度 (オフセット適用済み)")
for group_id in leg_config.CONNECTED_LEGS:
    leg_config.set_angle(group_id, "j2", 220)
    time.sleep(0.3)

# 最後に J3 を 40度に (大きく回転するので最後)
print("J3 (270度) -> 40度 (オフセット適用済み)")
for group_id in leg_config.CONNECTED_LEGS:
    leg_config.set_angle(group_id, "j3", 40)
    time.sleep(0.3)

input("\n収納姿勢になりました。Enterで終了 (サーボの保持トルクが切れる)")

leg_config.deinit()
print("完了")
