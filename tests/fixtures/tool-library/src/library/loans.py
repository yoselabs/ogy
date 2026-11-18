"""The tool library's loans: a stand-in the knowledge base fixture's `code:` sources name."""


class Tool:
    """A tool the library owns."""


class Loan:
    """One tool lent to one member."""


def lend() -> bool:
    return True


def late_fee(days: int) -> int:
    return 2 * max(days, 0)


def take_back() -> bool:
    return True
