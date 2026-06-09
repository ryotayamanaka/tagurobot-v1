"""脚とサーボのチャネル設定 + PCA9685 2枚のハブ (複数スクリプトで共有)。

group_id (0-5) で脚を識別する。1脚追加するたびに CONNECTED_LEGS を更新する。

## ボード構成 (元設計通り / ASSEMBLY_GUIDE.md §6-5)

    PCA9685 #1 (0x40): J3×6 = ch0-5,  J2×6 = ch6-11
    PCA9685 #2 (0x41): J1×6 = ch0-5

2枚目 (0x41) は A0 ジャンパーを短絡して設定する。

## このモジュールの役割

各スクリプトは PCA9685 を直接初期化せず、ここの
`get_servo()` / `set_angle()` 経由でサーボを操作する。
ボードの選択・チャネル・可動範囲・オフセットを一元管理する。

    import leg_config
    leg_config.set_angle(group_id, "j3", 135)   # オフセット適用込み
    ...
    leg_config.deinit()                          # 終了時に両ボード解放

実機 (Raspberry Pi) でのみハードウェアを初期化する。import 時には
何もせず、最初に get_servo/set_angle が呼ばれた時点で遅延初期化する。

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

# I2C アドレス
PCA1_ADDRESS = 0x40  # J3 (ch0-5) + J2 (ch6-11)
PCA2_ADDRESS = 0x41  # J1 (ch0-5)

# 各関節の可動範囲 (actuation_range)
# J2 の 270° 統一は 6脚化と同時に行う予定 (THREE_LEG_PROTOTYPE.md §8-A)。
# それまでは現状の 180° のまま。
JOINT_RANGE = {
    "j1": 180,
    "j2": 180,
    "j3": 270,
}


def get_j3_channel(group_id):
    """J3 (先端, 270度サーボ) のチャネル番号 - PCA9685 #1 の ch0-5"""
    return group_id


def get_j2_channel(group_id):
    """J2 (中間, 180度サーボ) のチャネル番号 - PCA9685 #1 の ch6-11"""
    return 6 + group_id


def get_j1_channel(group_id):
    """J1 (根元, 180度サーボ) のチャネル番号 - PCA9685 #2 の ch0-5"""
    return group_id


# (board_index, channel) を返すマップ。board_index: 1 = PCA #1(0x40), 2 = PCA #2(0x41)
def _joint_board_and_channel(group_id, joint):
    if joint == "j3":
        return 1, get_j3_channel(group_id)
    if joint == "j2":
        return 1, get_j2_channel(group_id)
    if joint == "j1":
        return 2, get_j1_channel(group_id)
    raise ValueError(f"不明な関節: {joint}")


def leg_name(group_id):
    """group_id から脚名 (A〜F) を返す"""
    return "ABCDEF"[group_id]


# ---------------------------------------------------------------------------
# キャリブレーション (取り付け誤差オフセット)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# PCA9685 2枚のハブ (遅延初期化)
# ---------------------------------------------------------------------------

_boards = {}   # board_index -> PCA9685
_servos = {}   # (group_id, joint) -> servo.Servo
_i2c = None


def _ensure_boards():
    """両ボードを (まだなら) 初期化する。実機でのみ呼ばれる前提。"""
    global _i2c
    if _boards:
        return
    import busio
    from adafruit_pca9685 import PCA9685
    from board import SCL, SDA

    _i2c = busio.I2C(SCL, SDA)
    pca1 = PCA9685(_i2c, address=PCA1_ADDRESS)
    pca1.frequency = 50
    pca2 = PCA9685(_i2c, address=PCA2_ADDRESS)
    pca2.frequency = 50
    _boards[1] = pca1
    _boards[2] = pca2


def get_servo(group_id, joint):
    """指定の脚・関節の servo.Servo を返す (キャッシュ付き)。

    正しいボード (0x40 / 0x41) とチャネル・可動範囲を自動で選ぶ。
    """
    key = (group_id, joint)
    if key in _servos:
        return _servos[key]

    _ensure_boards()
    from adafruit_motor import servo

    board_index, channel = _joint_board_and_channel(group_id, joint)
    s = servo.Servo(
        _boards[board_index].channels[channel],
        min_pulse=500,
        max_pulse=2500,
        actuation_range=JOINT_RANGE[joint],
    )
    _servos[key] = s
    return s


def set_angle(group_id, joint, logical_angle):
    """論理角度 (オフセット未適用) を指示する。オフセットを適用して返す。

    戻り値: 実際にサーボへ送った角度 (オフセット適用済み)。
    """
    actual = apply_offset(logical_angle, group_id, joint)
    get_servo(group_id, joint).angle = actual
    return actual


def deinit():
    """初期化済みの全ボードを解放する。"""
    for pca in _boards.values():
        pca.deinit()
    _boards.clear()
    _servos.clear()
