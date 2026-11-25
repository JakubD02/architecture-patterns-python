from datetime import datetime, timedelta

import pytest

from model import Batch, OrderLine, OutOfStock, allocate

today = datetime.now()
tomorrow = datetime.now() + timedelta(days=1)
later = datetime.now() + timedelta(days=3)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock", "TABLE-DESK", 100, eta=None)
    shipment_batch = Batch("shipment", "TABLE-DESK", 100, eta=tomorrow)
    line = OrderLine("oref", "TABLE-DESK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earlier = Batch("in-stock", "TABLE-DESK", 100, eta=today)
    medium = Batch("shipment", "TABLE-DESK", 100, eta=tomorrow)
    latest = Batch("shipment", "TABLE-DESK", 100, eta=later)
    line = OrderLine("oref", "TABLE-DESK", 10)

    allocate(line, [earlier, medium, latest])

    assert earlier.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock", "TABLE-DESK", 100, eta=None)
    shipment_batch = Batch("shipment", "TABLE-DESK", 100, eta=tomorrow)
    line = OrderLine("oref", "TABLE-DESK", 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    in_stock_batch = Batch("in-stock", "COFFEE-DESK", 20, eta=None)
    allocate(OrderLine("oref1", "COFFEE-DESK", 20), [in_stock_batch])

    with pytest.raises(OutOfStock, match="COFFEE"):
        allocate(OrderLine("oref2", "COFFEE-DESK", 1), [in_stock_batch])
