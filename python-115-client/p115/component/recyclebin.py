#!/usr/bin/env python3
# encoding: utf-8

__author__ = "ChenyangGao <https://chenyanggao.github.io>"
__all__ = ["P115Recyclebin"]

from collections.abc import Iterable, Iterator

from .client import check_response, P115Client


class P115Recyclebin:
    __slots__ = ("client", "password")

    def __init__(
        self, 
        client: P115Client, 
        /, 
        password: int | str = "", 
    ):
        self.client = client
        self.password = password

    def __contains__(self, id: int | str, /) -> bool:
        ids = str(id)
        return any(item["id"] == ids for item in self)

    def __delitem__(self, id: int | str, /):
        return self.remove(id)

    def __getitem__(self, id: int | str, /) -> dict:
        ids = str(id)
        for item in self:
            if item["id"] == ids:
                return item
        raise LookupError(f"no such id: {id!r}")

    def __iter__(self, /) -> Iterator[dict]:
        return self.iter()

    def __len__(self, /) -> int:
        return int(check_response(self.client.recyclebin_list({"limit": 1}))["count"])

    def __repr__(self, /) -> str:
        cls = type(self)
        module = cls.__module__
        name = cls.__qualname__
        if module != "__main__":
            name = module + "." + name
        return f"<{name}(client={self.client!r}) at {hex(id(self))}>"

    @check_response
    def clear(
        self, 
        /, 
        password: None | int | str = None, 
    ) -> dict:
        if password is None:
            password = self.password
        return self.client.recyclebin_clean({"password": password})

    def get(
        self, 
        id: int | str, 
        /, 
        default=None, 
    ):
        ids = str(id)
        return next((item for item in self if item["id"] == ids), default)

    def iter(
        self, 
        /, 
        offset: int = 0, 
        page_size: int = 1 << 10, 
    ) -> Iterator[dict]:
        if offset < 0:
            offset = 0
        if page_size <= 0:
            page_size = 1 << 10
        payload = {"offset": offset, "limit": page_size}
        count = 0
        while True:
            resp = check_response(self.client.recyclebin_list(payload))
            if resp["offset"] != payload["offset"]:
                return
            if count == 0:
                count = int(resp["count"])
            elif count != int(resp["count"]):
                raise RuntimeError("detected count changes during iteration")
            yield from resp["data"]
            if len(resp["data"]) < resp["page_size"]:
                return
            payload["offset"] += resp["page_size"]

    def list(
        self, 
        /, 
        offset: int = 0, 
        limit: int = 0, 
    ) -> list[dict]:
        if limit <= 0:
            return list(self.iter(offset))
        resp = check_response(self.client.recyclebin_list({"offset": offset, "limit": limit}))
        if resp["offset"] != offset:
            return []
        return resp["data"]

    @check_response
    def remove(
        self, 
        ids: int | str | Iterable[int | str], 
        /, 
        password: None | int | str = None, 
    ) -> dict:
        if isinstance(ids, (int, str)):
            payload = {"rid[0]": ids}
        else:
            payload = {f"rid[{i}]": id for i, id in enumerate(ids)}
        payload["password"] = self.password if password is None else password
        return self.client.recyclebin_clean(payload)

    @check_response
    def revert(
        self, 
        ids: int | str | Iterable[int | str], 
        /, 
    ) -> dict:
        if isinstance(ids, (int, str)):
            payload = {"rid[0]": ids}
        else:
            payload = {f"rid[{i}]": id for i, id in enumerate(ids)}
        return self.client.recyclebin_revert(payload)

