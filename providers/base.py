#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from collections import UserList
from typing import Optional
from datetime import datetime
from enum import Enum
import os
import yaml


CACHE_DIR = Path('cache')

log = print

##### IMAGE DATA #####


class StatusEnum(Enum):
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



class ProviderBase(UserList):
	SHORT_NAME = "base"


	DATA_DIR = CACHE_DIR / SHORT_NAME
	IMG_DIR = DATA_DIR / 'imgs'
	DATA_FILE = DATA_DIR / f'{SHORT_NAME}.yaml'

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
	def set_file_date(f: Path, date: str):
		a_time = f.stat().st_mtime
		m_time = datetime.strptime(date, '%Y%m%d').timestamp()
		os.utime(f, (a_time, m_time))
