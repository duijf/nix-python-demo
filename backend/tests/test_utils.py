import pytest

from api.utils import ignore_exc, maybe, maybe_ignore_exc


def test_ignore_exc() -> None:
    assert ignore_exc(int, ValueError, "foo") is None
    assert ignore_exc(int, ValueError, "42") == 42
    with pytest.raises(ValueError):
        ignore_exc(int, TypeError, "foo")  # Not caught, escapes.
    with pytest.raises(TypeError):
        ignore_exc(int, ValueError, None)  # type: ignore


def test_maybe() -> None:
    assert maybe(int, "42") == 42
    assert maybe(int, None) is None
    with pytest.raises(ValueError):
        maybe(int, "foo")


def test_maybe_ignore_exc() -> None:
    assert maybe_ignore_exc(int, ValueError, "42") == 42
    assert maybe_ignore_exc(int, ValueError, "foo") is None
    assert maybe_ignore_exc(int, ValueError, None) is None

    with pytest.raises(ValueError):
        maybe_ignore_exc(int, TypeError, "foo")  # Not caught, escapes.
