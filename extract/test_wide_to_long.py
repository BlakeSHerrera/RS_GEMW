'''Run this test via `pytest` on the terminal.'''


from typing import Iterable

import pytest

import main


def dict_set[T, U](dicts: Iterable[dict[T, U]]) -> set[tuple[T, U]]:
    '''
    A list of dicts cannot be turned into a set, so this function turns
    it into a comparable, sorted, human-searchable equivalent.
    '''
    return sorted(map(dict.items, dicts))


@pytest.fixture
def data_in() -> dict:
    return {
        "%LAST_UPDATE%": 1780020530,
        "%LAST_UPDATE_F%": "29 May 2026 02:08:50 (UTC)",
        "Abyssal whip": 90000,
        "Dragon scimitar": 125000
    }

@pytest.fixture
def data_out() -> list[dict]:
    return [
        {
            "%LAST_UPDATE%": 1780020530,
            "%LAST_UPDATE_F%": "29 May 2026 02:08:50 (UTC)",
            "name": "Abyssal whip",
            "value": 90000
        },
        {
            "%LAST_UPDATE%": 1780020530,
            "%LAST_UPDATE_F%": "29 May 2026 02:08:50 (UTC)",
            "name": "Dragon scimitar",
            "value": 125000
        }
    ]

def test_wide_to_long(data_in: dict, data_out: list[dict]):
    actual = main.wide_to_long(data_in)
    assert dict_set(actual) == dict_set(data_out)


def test_func_purity(data_in: dict):
    original = data_in.copy()
    main.wide_to_long(data_in)
    assert data_in == original
    