from omspy.models import *
import pytest


def test_basic_position():
    position = BasicPosition(symbol="AAPL")
    assert position.symbol == "AAPL"


def test_basic_position_calculations():
    position = BasicPosition(
        symbol="AAPL",
        buy_quantity=100,
        sell_quantity=120,
        buy_value=100 * 131,
        sell_value=120 * 118.5,
    )
    assert position.net_quantity == -20
    assert position.average_buy_value == 131
    assert position.average_sell_value == 118.5


def test_basic_position_zero_quantity():
    position = BasicPosition(symbol="AAPL")
    assert position.average_buy_value == 0
    assert position.average_sell_value == 0
    position.buy_quantity = 10
    assert position.average_buy_value == 0
    position.buy_value = 1315
    assert position.average_buy_value == 131.5
    assert position.average_sell_value == 0
