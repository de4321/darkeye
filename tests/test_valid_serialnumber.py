import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.utils import is_valid_serialnumber

@pytest.mark.parametrize("code, expected", [
    ("ABP-123", True),
    ("IPX-1024", True),
    ("SSNI-009", True),
    ("CAWD-999", True),
    ("abp-123", True),          # 小写也有效
    ("A-123", False),           # 前缀至少2个字母
    ("ABP-123456", False),      # 数字最多5位
    ("ABP123", False),          # 缺少 -
    ("ABP-12A", False),         # 数字中含字母不合法
    ("AB-1", True),             # 两位字母，1位数字
    ("ABCDEFG-123", False),     # 字母超过6位不合法
])
def test_is_valid_serialnumber(code, expected):
    assert is_valid_serialnumber(code) == expected


from utils.utils import covert_fanza
@pytest.mark.parametrize("input_code, expected", [
    ("IPX-247", "ipx00247"),
    ("ABP-123", "abp00123"),
    ("SSNI-009", "ssni00009"),
    ("CAWD-999", "cawd00999"),
    ("XYZ-1",   "xyz001"),
    ("NoDash",  "nodash"),
    ("abc-DEF", "abc00def"),
])
def test_covert_fanza(input_code, expected):
    assert covert_fanza(input_code) == expected