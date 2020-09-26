#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from collections import UserList
from typing import Optional, Union
from datetime import datetime, date
from enum import Enum
import os
import re
import yaml


CACHE_DIR = Path('cache')

log = print


date_t = Union[str, date, datetime]

##### IMAGE DATA #####


class StatusEnum(Enum):
	UNPROCESSED = 'UNPROCESSED'
	OK = 'OK'

	# General errors when handling the page
	ERROR = 'ERROR'	# General error while processing
	ERROR_DOWNLOADING = 'ERROR_DOWNLOADING'


@dataclass
class ImageBase:
	date: date_t
	url: str
	f_name: str

	# local FS data
	local: Optional[Path] = field(init=False)
	len: Optional[int] = field(init=False)
	hash: Optional[str] = field(init=False)



##### PROVIDER CLASS #####



class ProviderBase(UserList):
	SHORT_NAME = "base"


	DATA_DIR = CACHE_DIR / SHORT_NAME
	IMG_DIR = DATA_DIR / 'imgs'
	DATA_FILE = DATA_DIR / f'{SHORT_NAME}.yaml'

	DATE_FMT = "%Y%m%d"
	DATETIME_FMT = "%Y%m%d_%H%M%S"

	data: list[ImageBase]


	def dump(self):
		log(f"{self.__class__.__name__}: Dumping data (file={self.DATA_FILE})")
		yaml.dump(self.data, self.DATA_FILE.open('w'))

	def load(self):
		log(f"{self.__class__.__name__}: Loading data (file={self.DATA_FILE})")
		self.data = yaml.unsafe_load(self.DATA_FILE.open())

	def download(self):
		self.data = self.download_info()
		self.dump()

	def download_info(self, save_raw=True):
		raise NotImplementedError

	@staticmethod
	def set_file_date(f: Path, d: datetime):
		a_time = f.stat().st_mtime
		m_time = d.timestamp()
		os.utime(f, (a_time, m_time))


	_iso_format_pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
	@classmethod
	def is_iso_format(cls, d: str):
		return bool(cls._iso_format_pattern.match(d))

	@classmethod
	def date_to_str(cls, d: date_t) -> str:
		if isinstance(d, str):
			return d
		return d.strftime(cls.DATE_FMT)

	@classmethod
	def to_date(cls, d: date_t) -> date:
		if isinstance(d, date):
			return d
		elif isinstance(d, datetime):
			return d.date() 	# type: ignore
		elif isinstance(d, str):
			if cls.is_iso_format(d):
				return date.fromisoformat(d)
			return datetime.strptime(d, cls.DATE_FMT).date()
		else:
			raise TypeError

	@classmethod
	def to_datetime(cls, d: date_t) -> datetime:
		if isinstance(d, datetime):
			return d
		elif isinstance(d, date):
			return datetime(*d.timetuple()[:3])	# type: ignore
		elif isinstance(d, str):
			if cls.is_iso_format(d):
				return datetime.fromisoformat(d)
			return datetime.strptime(d, cls.DATETIME_FMT)
		else:
			raise TypeError

