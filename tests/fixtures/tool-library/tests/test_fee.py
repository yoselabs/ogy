"""The tool library's own test that its rule late-fee-is-per-day names as its proof (ogy's gate does not collect it)."""

from library.loans import late_fee


def test_late_fee_per_day() -> None:
    assert late_fee(3) == 6
