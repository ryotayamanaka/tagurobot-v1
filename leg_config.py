"""脚とサーボのチャネル設定 (複数スクリプトで共有)。

group_id (0-5) で脚を識別する。1脚追加するたびに CONNECTED_LEGS を更新する。

calibration.json には各サーボのオフセット (取り付け誤差の補正値) が
保存されている。apply_offset で論理角度に補正を加える。
"""
import json
import os

# 現在物理的に接続されている脚 (group_id のリスト)
# 1脚目: 脚A (group_id=0)
# 2脚目: 脚C (group_id=2)
# 3脚目: 脚E (group_id=4)
CONNECTED_LEGS = [0, 2, 4]


def get_j3_channel(group_id):
    """J3 (先端, 270度サーボ) のチャネル番号 - PCA9685 #1 の ch0-5"""
    return group_id


def get_j2_channel(group_id):
    """J2 (中間, 180度サーボ) のチャネル番号 - PCA9685 #1 の ch6-11"""
    return 6 + group_id


# J1 のチャネル割当 (暫定: PCA9685 #1 に詰め込み)
# main.py の元設計では group_id ごとに連続だが、PCA9685 1枚に
# 18サーボは入らないので、3脚目以降は空きチャネルを借りる。
# フル構成では PCA9685 #2 を導入し、group_id 通りに割り当てる。
J1_CHANNEL_MAP = {
    0: 12,  # 脚A (元設計通り)
    1: 13,  # 脚B (元設計通り)
    2: 14,  # 脚C (元設計通り)
    3: 15,  # 脚D (元設計通り)
    4: 11,  # 脚E ← 空きを借りる (脚F J2 と将来衝突するので2枚目導入時に再配置)
    5: 5,   # 脚F ← 空きを借りる (脚F J3 と将来衝突するので2枚目導入時に再配置)
}


def get_j1_channel(group_id):
    """J1 (根元, 180度サーボ) のチャネル番号

    暫定: PCA9685 #1 に詰め込み
    フル構成時: PCA9685 #2 の ch0-5 に移行する (このマップを書き換える)
    """
    return J1_CHANNEL_MAP[group_id]


def leg_name(group_id):
    """group_id から脚名 (A〜F) を返す"""
    return "ABCDEF"[group_id]


CALIBRATION_FILE = os.path.join(os.path.dirname(__file__), "calibration.json")


def load_calibration():
    """calibration.json を読み込む。存在しなければ空辞書。"""
    if not os.path.exists(CALIBRATION_FILE):
        return {}
    with open(CALIBRATION_FILE) as f:
        return json.load(f)


# プロセス起動時に1度だけ読み込んでキャッシュ
_calibration_cache = load_calibration()


def get_offset(group_id, joint):
    """指定の脚・関節のオフセットを返す (未設定なら0)。

    joint は "j1" / "j2" / "j3" のいずれか。
    """
    return _calibration_cache.get(str(group_id), {}).get(joint, 0)


def apply_offset(angle, group_id, joint):
    """論理角度にオフセットを適用して実際のサーボ指示角度を返す。"""
    return angle + get_offset(group_id, joint)
