"""The tool library's own test that its entity loan names as its proof (ogy's gate does not collect it)."""

from library.loans import lend, take_back


def test_loan_lifecycle() -> None:
    assert lend()
    assert take_back()
