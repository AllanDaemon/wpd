#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from collections import UserList
from typing import Optional, Union
from datetime import datetime, date
from enum import Enum
from hashlib import sha256
from PIL import Image
from threading import Thread
from queue import Queue
import os
import re
import yaml

import requests


Image.MAX_IMAGE_PIXELS = None	# type: ignore


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
	local: Optional[Path] = field(init=False, default=None)
	size: Optional[int] = field(init=False, default=None)
	hash: Optional[str] = field(init=False, default=None)
	format: Optional[str] = field(init=False, default=None)
	resolution: Optional[tuple[int, int]] = field(init=False, default=None)
	# w x h


	@property
	def file(self) -> Optional[Path]:
		if not self.local: return None
		return CACHE_DIR / self.local



##### PROVIDER CLASS #####

class ThreadWorkerPoll:
	num_workers: int = 3
	workers: list[Thread]
	queue: Queue
	running: bool = True

	def __init__(self, process_function, n: int = num_workers):
		self.num_workers = n
		self.process_function = process_function
		self.init_async()
		self.start()

	def init_async(self):
		self.queue = Queue()

		self.workers = [
			Thread(
				name = f'{type(self).__name__} Thread {i}',
				target = self.thread_loop,
				args = (i,),
				daemon = True,
			)
			for i in range(self.num_workers)
		]

	def start(self):
		for t in self.workers:
			t.start()

	def stop(self):
		self.running = False
		for t in self.workers:
			t.join()

	def put(self, elem):
		return self.queue.put(elem)

	def join(self):
		return self.queue.join()

	def thread_loop(self, i):
		log(f'Starting thread worker {i}')
		f = self.process_function
		while self.running:
			arg = self.queue.get()
			f(arg)
			self.queue.task_done()



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
		if not self.data:
			self.data = []
		self.data += self.download_info()
		self.dump()

	def download_info(self, save_raw=True):
		raise NotImplementedError

	@staticmethod
	def set_file_date(f: Path, d: datetime):
		a_time = f.stat().st_mtime
		m_time = d.timestamp()
		os.utime(f, (a_time, m_time))

	def _download_img_set(self, img, data, f_path):
		image = Image.open(f_path)
		img.local = f_path.relative_to(CACHE_DIR)
		img.size = len(data)
		img.hash = sha256(data).hexdigest()
		img.format = image.format
		img.resolution = image.size
		self.set_file_date(f_path, self.to_datetime(img.date))

	def download_image(self, img: ImageBase, overwrite: bool = False, auto_dump: bool = False):
		f_path = self.IMG_DIR / img.f_name
		log(f'{self.__class__.__name__}:',
			f'Downloading img [{self.date_to_str(img.date)}] "{img.url}"')

		if not overwrite:
			if img.local:
				log(f'\t\tSKIPPED (saved path) {f_path}')
				return
			elif f_path.is_file():
				log(f'\t\tSKIPPED (exists on FS) {f_path}')
				data = f_path.read_bytes()
				self._download_img_set(img, data, f_path)
				return

		res = requests.get(img.url)
		assert res.status_code == 200
		log(f'\t\t{len(res.content)}bytes -> {f_path}')
		f_path.write_bytes(res.content)
		self._download_img_set(img, res.content, f_path)

		if auto_dump:
			self.dump()

	def download_images(self,
						images: Optional[list[ImageBase]] = None,
						overwrite: bool = False,
						auto_dump: bool = True,
	):
		log(f"{self.__class__.__name__}: Downloading images")
		if not images:
			images = self.data

		for img in images:
			self.download_image(img, overwrite=overwrite, auto_dump=False)

		if auto_dump:
			self.dump()

	def download_images_async(self,
						images: Optional[list[ImageBase]] = None,
						overwrite: bool = False,
						auto_dump: bool = True,
						n_jobs: int = 8,
	):
		log(f"{self.__class__.__name__}: Downloading images async")
		if not images:
			images = self.data

		pool = ThreadWorkerPoll(self.download_image, n_jobs)

		for img in images:
			pool.put(img)
			# self.download_image(img, overwrite=overwrite, auto_dump=False)
		try:
			pool.join()
		except:
			pool.stop()

		if auto_dump:
			self.dump()


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
			try:
				return datetime.strptime(d, cls.DATETIME_FMT)
			except ValueError:
				d = cls.to_date(d)
				return cls.to_datetime(d)
		else:
			raise TypeError

