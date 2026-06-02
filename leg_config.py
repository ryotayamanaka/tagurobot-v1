"""脚とサーボのチャネル設定 (複数スクリプトで共有)。

group_id (0-5) で脚を識別する。1脚追加するたびに CONNECTED_LEGS を更新する。
"""

# 現在物理的に接続されている脚 (group_id のリスト)
# 1脚目: 脚A (group_id=0)
# 2脚目: 脚C (group_id=2)
CONNECTED_LEGS = [0, 2]


def get_j3_channel(group_id):
    """J3 (先端, 270度サーボ) のチャネル番号 - PCA9685 #1 の ch0-5"""
    return group_id


def get_j2_channel(group_id):
    """J2 (中間, 180度サーボ) のチャネル番号 - PCA9685 #1 の ch6-11"""
    return 6 + group_id


def get_j1_channel(group_id):
    """J1 (根元, 180度サーボ) のチャネル番号

    暫定: PCA9685 #1 の ch12-15 を使用
    フル構成時: PCA9685 #2 の ch0-5 に移行する (この関数を書き換える)
    """
    return 12 + group_id


def leg_name(group_id):
    """group_id から脚名 (A〜F) を返す"""
    return "ABCDEF"[group_id]
