import asyncio
import threading

from tui_engine.defaults import DefaultApplier, DependencyMap


def test_dependency_map_set_if_absent_single_thread() -> None:
    dm = DependencyMap()

    called: dict[str, int] = {"n": 0}

    def factory() -> str:
        called["n"] += 1
        return "v"

    v1 = dm.set_if_absent("k", factory)
    v2 = dm.set_if_absent("k", factory)

    assert v1 == "v"
    assert v2 == "v"
    # factory called only once because second time value present
    assert called["n"] == 1


def test_dependency_map_set_if_absent_concurrent() -> None:
    dm = DependencyMap()

    def factory() -> str:
        # slight delay to expose race if any
        return "computed"

    results: list[str] = []

    def worker() -> None:
        results.append(dm.set_if_absent("k", factory))

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(r == "computed" for r in results)
    assert dm.get("k") == "computed"


def test_default_applier_with_sync_factory() -> None:
    target: dict[str, object] = {}
    applier = DefaultApplier(target)

    def factory() -> int:
        return 123

    v = applier.apply("a", factory)
    assert v == 123
    assert target["a"] == 123


def test_default_applier_with_async_factory() -> None:
    target: dict[str, object] = {}
    applier = DefaultApplier(target)

    async def afactory() -> str:
        await asyncio.sleep(0)
        return "async-val"

    # apply should await the coroutine and set the value
    v = applier.apply("b", afactory)
    assert v == "async-val"
    assert target["b"] == "async-val"
