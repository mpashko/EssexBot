import pytest

from modules.exchange_rate import XrateHandler


def test_convert_to_str():
    xhandler = XrateHandler()
    assert xhandler._convert_to_str(1) == '1'
    assert xhandler._convert_to_str(10) == '10'
    assert xhandler._convert_to_str(100) == '100'
    assert xhandler._convert_to_str(1000) == '1 000'
    assert xhandler._convert_to_str(10000) == '10 000'
    assert xhandler._convert_to_str(100000) == '100 000'
    assert xhandler._convert_to_str(1000000) == '1 000 000'
    assert xhandler._convert_to_str(1.1) == '1.1'
    assert xhandler._convert_to_str(10.1) == '10.1'
    assert xhandler._convert_to_str(100.1) == '100.1'
    assert xhandler._convert_to_str(1000.1) == '1 000.1'
    assert xhandler._convert_to_str(10000.1) == '10 000.1'
    assert xhandler._convert_to_str(100000.1) == '100 000.1'
    assert xhandler._convert_to_str(1000000.1) == '1 000 000.1'

    with pytest.raises(TypeError):
        xhandler._convert_to_str('1000')

    with pytest.raises(TypeError):
        xhandler._convert_to_str([])
