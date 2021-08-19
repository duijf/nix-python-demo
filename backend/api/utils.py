import typing as t

from funcy import partial  # type: ignore

T = t.TypeVar("T")
S = t.TypeVar("S")


def maybe(func: t.Callable[[S], T], val: t.Optional[S]) -> t.Optional[T]:
    """
    If `val` is `None`, return `None`. Otherwise apply `func`.
    """
    if val is None:
        return None

    return func(val)


def ignore_exc(
    func: t.Callable[[S], T], exc: t.Type[BaseException], val: S
) -> t.Optional[T]:
    """
    Apply `func` to `val`, returning `None` if exception `exc` is raised.
    """
    try:
        return func(val)
    except exc:
        return None


def maybe_ignore_exc(
    func: t.Callable[[S], T], exc: t.Type[BaseException], val: t.Optional[S]
) -> t.Optional[T]:
    """
    Apply `func` to `val`, returning the result.

    Returns `None` if `val` is `None`, or `func` raises `exc`.
    """
    return maybe(partial(ignore_exc, func, exc), val)
