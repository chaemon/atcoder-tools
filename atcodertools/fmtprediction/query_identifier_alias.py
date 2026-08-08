import copy
import dataclasses
import re
import string
from enum import Enum
from types import FunctionType, ModuleType
from typing import Dict, Mapping, Set, Tuple

from atcodertools.client.models.problem_content import (
    ProblemContent,
)


_INDEXED_DIGIT_BASE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])"
    r"([A-Za-z][A-Za-z0-9]*[0-9][A-Za-z0-9]*)"
    r"_(?=[A-Za-z0-9{])"
)

_ALPHA_RUN_PATTERN = re.compile(r"[A-Za-z]+")


def _alphabetic_suffix(index: int) -> str:
    chars = []
    value = index

    while True:
        value, remainder = divmod(value, 26)
        chars.append(string.ascii_lowercase[remainder])

        if value == 0:
            break

        value -= 1

    return "".join(reversed(chars))


def _allocate_alias(
    used_alpha_runs: Set[str],
    allocated: Set[str],
) -> str:
    index = 0

    while True:
        candidate = "zzq" + _alphabetic_suffix(index)
        index += 1

        if candidate in used_alpha_runs:
            continue

        if candidate in allocated:
            continue

        return candidate


def _replace_indexed_base(
    text: str,
    original: str,
    alias: str,
) -> str:
    pattern = re.compile(
        r"(?<![A-Za-z0-9])"
        + re.escape(original)
        + r"_(?=[A-Za-z0-9{])"
    )

    return pattern.sub(
        alias + "_",
        text,
    )


def encode_spliced_query_identifiers(
    content: ProblemContent,
) -> Tuple[ProblemContent, Dict[str, str]]:
    """Encode indexed bases that the existing FormatSearcher cannot parse."""

    input_format = content.get_input_format()

    originals = []
    seen = set()

    for match in _INDEXED_DIGIT_BASE_PATTERN.finditer(
        input_format
    ):
        original = match.group(1)

        if original in seen:
            continue

        seen.add(original)
        originals.append(original)

    if not originals:
        return content, {}

    used_alpha_runs = set(
        _ALPHA_RUN_PATTERN.findall(input_format)
    )
    allocated = set()
    alias_to_original = {}
    encoded = input_format

    for original in originals:
        alias = _allocate_alias(
            used_alpha_runs,
            allocated,
        )
        allocated.add(alias)
        alias_to_original[alias] = original
        encoded = _replace_indexed_base(
            encoded,
            original,
            alias,
        )

    return (
        ProblemContent(
            input_format_text=encoded,
            samples=content.get_samples(),
        ),
        alias_to_original,
    )


def _replace_alias_tokens(
    value: str,
    alias_to_original: Mapping[str, str],
) -> str:
    result = value

    for alias in sorted(
        alias_to_original,
        key=len,
        reverse=True,
    ):
        pattern = re.compile(
            r"(?<![A-Za-z0-9])"
            + re.escape(alias)
            + r"(?![A-Za-z0-9])"
        )
        result = pattern.sub(
            alias_to_original[alias],
            result,
        )

    return result


def _restore_graph(
    value,
    alias_to_original: Mapping[str, str],
    memo,
):
    if isinstance(value, str):
        return _replace_alias_tokens(
            value,
            alias_to_original,
        )

    if value is None or isinstance(
        value,
        (
            int,
            float,
            bool,
            bytes,
            Enum,
            type,
            FunctionType,
            ModuleType,
        ),
    ):
        return value

    object_id = id(value)

    if object_id in memo:
        return memo[object_id]

    if isinstance(value, tuple):
        restored_values = [
            _restore_graph(
                item,
                alias_to_original,
                memo,
            )
            for item in value
        ]

        if hasattr(value, "_fields"):
            restored = type(value)(
                *restored_values
            )
        else:
            restored = tuple(restored_values)

        memo[object_id] = restored
        return restored

    if isinstance(value, list):
        restored = [
            _restore_graph(
                item,
                alias_to_original,
                memo,
            )
            for item in value
        ]
        memo[object_id] = restored
        return restored

    if isinstance(value, dict):
        restored = {
            _restore_graph(
                key,
                alias_to_original,
                memo,
            ): _restore_graph(
                item,
                alias_to_original,
                memo,
            )
            for key, item in value.items()
        }
        memo[object_id] = restored
        return restored

    if isinstance(value, set):
        restored = {
            _restore_graph(
                item,
                alias_to_original,
                memo,
            )
            for item in value
        }
        memo[object_id] = restored
        return restored

    if isinstance(value, frozenset):
        restored = frozenset(
            _restore_graph(
                item,
                alias_to_original,
                memo,
            )
            for item in value
        )
        memo[object_id] = restored
        return restored

    if (
        dataclasses.is_dataclass(value)
        and not isinstance(value, type)
    ):
        changes = {
            field.name: _restore_graph(
                getattr(value, field.name),
                alias_to_original,
                memo,
            )
            for field in dataclasses.fields(value)
        }

        restored = dataclasses.replace(
            value,
            **changes
        )
        memo[object_id] = restored
        return restored

    if hasattr(value, "__dict__"):
        restored = copy.copy(value)
        memo[object_id] = restored

        for name, item in vars(value).items():
            restored_item = _restore_graph(
                item,
                alias_to_original,
                memo,
            )

            try:
                setattr(
                    restored,
                    name,
                    restored_item,
                )
            except Exception:
                object.__setattr__(
                    restored,
                    name,
                    restored_item,
                )

        return restored

    return value


def restore_identifier_aliases(
    value,
    alias_to_original: Mapping[str, str],
):
    if not alias_to_original:
        return value

    restored = _restore_graph(
        value,
        alias_to_original,
        {},
    )

    rendered = str(restored)

    leaked = [
        alias
        for alias in alias_to_original
        if alias in rendered
    ]

    if leaked:
        raise ValueError(
            "identifier aliases leaked after restore: "
            + ", ".join(sorted(leaked))
        )

    return restored
