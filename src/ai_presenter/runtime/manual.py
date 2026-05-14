from collections import deque
from dataclasses import dataclass
from typing import Literal


DirectiveKind = Literal["say", "skip", "focus"]


@dataclass(frozen=True)
class ManualDirective:
    kind: DirectiveKind
    text: str


class ManualDirectiveQueue:
    def __init__(self) -> None:
        self._directives: deque[ManualDirective] = deque()

    def submit(self, raw_text: str) -> None:
        directive = _parse_directive(raw_text)
        if directive is not None:
            self._directives.append(directive)

    def consume_next(self) -> ManualDirective | None:
        if not self._directives:
            return None
        return self._directives.popleft()

    def peek_next(self) -> ManualDirective | None:
        if not self._directives:
            return None
        return self._directives[0]


def _parse_directive(raw_text: str) -> ManualDirective | None:
    text = raw_text.strip()
    if not text:
        return None

    lowered = text.casefold()
    if lowered == "skip" or lowered.startswith("skip:"):
        return ManualDirective("skip", _directive_payload(text))
    if lowered.startswith("say:"):
        payload = _directive_payload(text)
        if payload:
            return ManualDirective("say", payload)
        return None
    if lowered.startswith("focus:"):
        payload = _directive_payload(text)
        if payload:
            return ManualDirective("focus", payload)
        return None
    return ManualDirective("say", text)


def _directive_payload(text: str) -> str:
    _, separator, payload = text.partition(":")
    if not separator:
        return ""
    return payload.strip()
