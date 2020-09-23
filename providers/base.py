#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from collections import UserList
from typing import ClassVar, Optional


CACHE_DIR = Path('cache')

log = print

@dataclass
class ImageBase:
	date: str
	url: str
	f_name: str

	# local FS data
	local: Optional[Path] = field(init=False)
	len: Optional[int] = field(init=False)
	hash: Optional[str] = field(init=False)



class ProviderBaseMeta(type, UserList):

	@property
	def DATA_DIR(cls):
		return CACHE_DIR / cls.SHORT_NAME	# type: ignore

	@property
	def IMG_DIR(cls):
		return cls.DATA_DIR / 'imgs'

	@property
	def DATA_FILE(cls):
		return cls.DATA_DIR / f'{cls.SHORT_NAME}.yaml'	# type: ignore


class ProviderBase(metaclass=ProviderBaseMeta):
	SHORT_NAME = "base"

	# should be copied in subclasses otherwise pylint can't see it.
	DATA_DIR: ClassVar[Path]
	IMG_DIR: ClassVar[Path]
	DATA_FILE: ClassVar[Path]

	data: ClassVar[list[ImageBase]]
