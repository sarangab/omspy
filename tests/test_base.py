import json
import pytest
from unittest.mock import patch, call
import pendulum
from copy import deepcopy
from omspy.base import Broker, pre, post
from omspy.brokers.paper import Paper

# Load some mock data
with open("tests/data/kiteconnect/orders.json") as f:
    orders = json.load(f)["data"]
    for order in orders:
        order["status"] = "pending"
with open("tests/data/kiteconnect/trades.json") as f:
    trades = json.load(f)["data"]
with open("tests/data/kiteconnect/positions.json") as f:
    positions = json.load(f)["data"]["day"]


class Dummy(Broker):
    """
    Creating a dummy broker class to test base functions
    """

    def __init__(self, **kwargs):
        # Just adds the orders
        self._place_orders = []
        self._modify_orders = []
        self._cancel_orders = []
        super(Dummy, self).__init__(**kwargs)

    def authenticate(self):
        return "Authentication done"

    def order_place(self, **kwargs):
        self._place_orders.append(kwargs)
        return kwargs

    def order_modify(self, order_id, **kwargs):
        kwargs["order_id"] = order_id
        self._place_orders.append(kwargs)
        return order_id

    def order_cancel(self, order_id):
        self._cancel_orders.append(order_id)
        return order_id

    @property
    @post
    def orders(self):
        return orders

    @property
    @post
    def trades(self):
        return trades

    @property
    @post
    def positions(self):
        return positions


@pytest.fixture
def broker():
    return Dummy(override_file="tests/data/zerodha.yaml")


def test_dummy_broker_values(broker):
    assert broker.order_place(symbol="aapl") == {"symbol": "aapl"}
    assert broker.order_modify(1234) == 1234
    assert broker.order_cancel(1234) == 1234


def test_close_all_positions(broker):
    call_args = [
        dict(symbol="GOLDGUINEA17DECFUT", order_type="MARKET", quantity=3, side="buy"),
        dict(symbol="LEADMINI17DECFUT", order_type="MARKET", quantity=1, side="sell"),
    ]
    broker.close_all_positions()
    assert broker._place_orders[0] == call_args[0]
    assert broker._place_orders[1] == call_args[1]


def test_cancel_all_orders(broker):
    call_args = [
        "100000000000000",
        "300000000000000",
        "500000000000000",
        "700000000000000",
        "9000000000000000",
    ]
    broker.cancel_all_orders()
    for a, e in zip(broker._cancel_orders, call_args):
        assert a == e


def test_close_all_positions_copy_keys(broker):
    call_args = [
        dict(
            symbol="GOLDGUINEA17DECFUT",
            order_type="MARKET",
            quantity=3,
            side="buy",
            product="NRML",
            exchange="MCX",
        ),
        dict(
            symbol="LEADMINI17DECFUT",
            order_type="MARKET",
            quantity=1,
            side="sell",
            product="NRML",
            exchange="MCX",
        ),
    ]
    broker.close_all_positions(keys_to_copy=("exchange", "product"))
    assert broker._place_orders[0] == call_args[0]
    assert broker._place_orders[1] == call_args[1]


def test_close_all_positions_add_keys(broker):
    call_args = [
        dict(
            symbol="GOLDGUINEA17DECFUT",
            order_type="MARKET",
            quantity=3,
            side="buy",
            variety="regular",
        ),
        dict(
            symbol="LEADMINI17DECFUT",
            order_type="MARKET",
            quantity=1,
            side="sell",
            variety="regular",
        ),
    ]
    broker.close_all_positions(keys_to_add={"variety": "regular"})
    assert broker._place_orders[0] == call_args[0]
    assert broker._place_orders[1] == call_args[1]


def test_close_all_positions_copy_and_add_keys(broker):
    call_args = [
        dict(
            symbol="GOLDGUINEA17DECFUT",
            order_type="MARKET",
            quantity=3,
            side="buy",
            product="NRML",
            exchange="MCX",
            validity="day",
        ),
        dict(
            symbol="LEADMINI17DECFUT",
            order_type="MARKET",
            quantity=1,
            side="sell",
            product="NRML",
            exchange="MCX",
            validity="day",
        ),
    ]
    broker.close_all_positions(
        keys_to_copy=("exchange", "product"), keys_to_add={"validity": "day"}
    )
    assert broker._place_orders[0] == call_args[0]
    assert broker._place_orders[1] == call_args[1]


def test_cover_orders():
    orders = [
        dict(
            symbol="aapl",
            side="buy",
            quantity=10,
            filled_quantity=10,
            status="COMPLETE",
            average_price=160,
        ),
        dict(
            symbol="aapl",
            side="sell",
            quantity=5,
            filled_quantity=5,
            status="COMPLETE",
            average_price=150,
        ),
    ]
    broker = Paper(orders=orders)
    with patch("omspy.brokers.paper.Paper.order_place") as order_place:
        kwargs = dict(
            symbol="aapl", quantity=5, side="sell", price=152, order_type="LIMIT"
        )
        broker.cover_orders(stop=0.05)
        order_place.assert_called_once()
        print(order_place.call_args)


def test_cover_orders_multiple():
    orders = [
        dict(
            symbol="aapl",
            side="buy",
            quantity=10,
            filled_quantity=10,
            status="COMPLETE",
            average_price=160,
        ),
        dict(
            symbol="aapl",
            side="sell",
            quantity=5,
            filled_quantity=5,
            status="COMPLETE",
            average_price=150,
        ),
        dict(
            symbol="goog", side="sell", quantity=20, status="PENDING", trigger_price=100
        ),
    ]
    broker = Paper(orders=orders)
    with patch("omspy.brokers.paper.Paper.order_place") as order_place:
        kwargs = [
            dict(symbol="aapl", quantity=5, side="SELL", trigger_price=152, order_type="SL-M"),
            dict(symbol="goog", quantity=20, side="BUY", trigger_price=105, order_type="SL-M"),
        ]

        broker.cover_orders(stop=0.05)
        assert order_place.call_count == 2
        print(order_place.call_args_list)
        assert order_place.call_args_list[0] == call(**kwargs[0])
        assert order_place.call_args_list[1] == call(**kwargs[1])
