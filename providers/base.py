#!/usr/bin/env python3

from __future__ import annotations
from pathlib import Path
from collections import UserList


CACHE_DIR = Path('../cache')

log = print

class ImageBase:
	...


class ProviderBaseMeta(type, UserList): ...


class ProviderBase(metaclass=ProviderBaseMeta):
	...

