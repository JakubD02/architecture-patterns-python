from dataclasses import dataclass
from datetime import date
from typing import List, NewType, Optional

Quantity = NewType("Quantity", int)
Sku = NewType("Sku", str)
Reference = NewType("Reference", str)


@dataclass(frozen=True)
class OrderLine:
    order_id: Reference
    sku: Sku  # stock keeping unit
    quantity: Quantity


class OutOfStock(Exception):
    pass


class Batch:
    def __init__(
        self, ref: Reference, sku: Sku, quantity: Quantity, eta: Optional[date]
    ):
        self.reference = ref
        self.sku = sku
        self.eta = eta  # estimated time of arrival
        self._purchased_quantity = quantity
        self._allocations = set()

    def __setattr__(self, name, value):
        if name == "_purchased_quantity" and value < 0:
            raise ValueError(f"{name} must be >= 0")
        super().__setattr__(name, value)

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    @property
    def allocated_quantity(self) -> int:
        return sum(val.quantity for val in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.available_quantity >= line.quantity and self.sku == line.sku

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
