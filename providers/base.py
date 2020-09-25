#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from collections import UserList
from typing import ClassVar, Optional
from datetime import datetime
from enum import Enum
import os
import yaml


CACHE_DIR = Path('cache')

log = print

##### IMAGE DATA #####


class StatusEnum:
	UNPROCESSED = 'UNPROCESSED'
	OK = 'OK'

	# General errors when handling the page
	ERROR = 'ERROR'	# General error while processing
	ERROR_DOWNLOADING = 'ERROR_DOWNLOADING'


@dataclass
class ImageBase:
	date: str
	url: str
	f_name: str

	# local FS data
	local: Optional[Path] = field(init=False)
	len: Optional[int] = field(init=False)
	hash: Optional[str] = field(init=False)



##### PROVIDER CLASS #####

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


	@classmethod
	def dump(cls):
		log(f"{cls.__name__}: Dumping data (file={cls.DATA_FILE})")
		yaml.dump(cls.data, cls.DATA_FILE.open('w'))

	@classmethod
	def load(cls):
		log(f"{cls.__name__}: Loading data (file={cls.DATA_FILE})")
		cls.data = yaml.unsafe_load(cls.DATA_FILE.open())

	@classmethod
	def download(cls):
		cls.data = cls.download_info()
		cls.dump()

	@classmethod
	def download_info(cls, save_raw=True):
		raise NotImplementedError

	@staticmethod
	def set_file_date(f: Path, date: str):
		a_time = f.stat().st_mtime
		m_time = datetime.strptime(date, '%Y%m%d').timestamp()
		os.utime(f, (a_time, m_time))
