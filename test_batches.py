from datetime import date, timedelta
import pytest

from model import Batch, OrderLine

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty),
    )


def test_can_allocate_if_available_greater_than_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert batch.can_allocate(line)

    batch.allocate(line)
    assert batch.available_quantity == 18


def test_cannot_allocate_if_available_smaller_than_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 20, 50)
    assert batch.can_allocate(line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 20, 20)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "ELEGANT-CHAIR", 10, eta=date.today())
    diff_sku_line = OrderLine("order-123", "CHEAP-CHAIR", 3)
    assert batch.can_allocate(diff_sku_line) is False


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18
