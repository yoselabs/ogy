"""How a command ended: one verdict on every result, and the refusals that carry theirs."""

from enum import IntEnum


class Verdict(IntEnum):
    """The exit code of the CLI and the outcome over MCP (2 to 4 are tool errors there)."""

    OK = 0
    FINDINGS = 1  # the command ran and found something (check, work-left, a reply with an item refused)
    USAGE = 2  # the arguments or the settings are wrong
    REFUSED = 3  # understood, and not done
    NOT_FOUND = 4  # the entry or the round named does not exist


class RefusalError(Exception):
    """A command that stops before it changes anything. `reasons` say why, `lines()` print them."""

    verdict = Verdict.REFUSED
    prefix = "refused: "

    def __init__(self, reasons: list[str] | str) -> None:
        self.reasons = [reasons] if isinstance(reasons, str) else reasons
        super().__init__("; ".join(self.reasons))

    def lines(self) -> list[str]:
        return [f"{self.prefix}{reason}" for reason in self.reasons]


class NotFoundError(RefusalError):
    """The thing named does not exist."""

    verdict = Verdict.NOT_FOUND
    prefix = ""


class UnusableError(RefusalError):
    """The flags or settings cannot be used."""

    verdict = Verdict.USAGE
    prefix = ""


class MissingTargetError(RefusalError):
    """The knowledge base asked for is not there: its folder at that commit, or the commit."""

    prefix = ""
