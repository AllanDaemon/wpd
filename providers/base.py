#!/usr/bin/env python3

from __future__ import annotations
from pathlib import Path
from collections import UserList
from typing import ClassVar


CACHE_DIR = Path('cache')

log = print

class ImageBase:
	...


class ProviderBaseMeta(type, UserList):

	@property
	def DATA_DIR(cls):
		return CACHE_DIR / cls.SHORT_NAME

	@property
	def IMG_DIR(cls):
		return cls.DATA_DIR / 'imgs'

	@property
	def DATA_FILE(cls):
		return cls.DATA_DIR / f'{cls.SHORT_NAME}.yaml'


class ProviderBase(metaclass=ProviderBaseMeta):
	SHORT_NAME = "base"

	DATA_DIR: ClassVar[Path]
	IMG_DIR: ClassVar[Path]
	DATA_FILE: ClassVar[Path]


