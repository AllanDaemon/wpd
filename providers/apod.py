#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
from datetime import date as Date
from typing import ClassVar
from pathlib import Path

import requests

from .base import ImageBase, ProviderBase, CACHE_DIR, log


@dataclass
class ApodImage(ImageBase):
	# date: str
	# f_name: str
	# url: str



class ApodProvider(ProviderBase):
	SHORT_NAME = 'apod'

	# For pylint sakes
	DATA_DIR: ClassVar[Path]
	IMG_DIR: ClassVar[Path]
	DATA_FILE: ClassVar[Path]
	data: ClassVar[list[ImageBase]]

	PAGE_DIR: ClassVar[Path] = DATA_DIR / 'pages'
	ARCHIVE_URL = "https://apod.nasa.gov/apod/archivepix.html"
	FULL_ARCHIVE_URL = "https://apod.nasa.gov/apod/archivepixFull.html"
	# DATE_URL = "https://apod.nasa.gov/apod/ap%y%m%d.html"
	DATE_URL_BASE = "https://apod.nasa.gov/apod/ap%y%m%d.html"
	DATE_FNAME_BASE = 'ap%y%m%d.html'



	@classmethod
	def get_day_info(cls, date: Date, cache=PAGE_DIR):
		log(f"{cls.__name__}: Getting day info ({date=})")

		f_name = date.strftime(cls.DATE_FNAME_BASE)

		if cache and (cache / f_name).is_file():
			page = (cache / f_name).read_str()
		else:
			page = cls.download_day_page(date)

		return cls.parse_day_page(page)

	@classmethod
	def download_day_page(cls, date:Date, cache=PAGE_DIR, save_raw=True) -> str:
		log(f"{cls.__name__}: Downloading day pages ({date=})")
	
		url = date.strftime(cls.DATE_URL_BASE)
		res = requests.get(url)
		assert res.status_code == 200

		if save_raw:
			f_path = cache / Path(url).name
			log(f"{cls.__name__}: \tSaving arquive (file={f_path})")
			f_path.write_bytes(res.content)
		
		return res.text

	@classmethod
	def parse_day_page(cls, page: str, date:Date):
		...

	@classmethod
	def download_archive_info(cls, full_archive=False, save_raw=True):
		log(f"{cls.__name__}: Downloading archive info ({full_archive=})")

		url = cls.ARCHIVE_URL if not full_archive else cls.FULL_ARCHIVE_URL
		res = requests.get(url)
		assert res.status_code == 200

		if save_raw:
			_f_name = Path(url)
			f_path = cls.DATA_DIR / _f_name.name
			log(f"{cls.__name__}: \tSaving arquive (file={f_path})")
			f_path.write_bytes(res.content)

		entries_raw = res.text 	#PARSE
		entries = list()
		return entries


	@classmethod
	def process_image_info(cls, info: dict) -> ApodImage:
		return ApodImage(
			# date = info['startdate'],
			# title = info['title'],
			# about = info['copyright'],
			# _hash = info['hsh'],
			# url_path = info['url'],
			# url = cls.BASE_IMG_URL + info['url'],
			# f_name = f_name,
			# extension = ext,
			# id_str = id_str,
			# id_num = id_num,
			# resolution = res,
		)

	@classmethod
	def download_images(cls, overwrite: bool = False, auto_dump: bool = True):
		log(f"{cls.__name__}: Downloading images")
		for img in cls.data:
			f_path = cls.IMG_DIR / img.f_name
			log(f'{cls.__name__}:\tDownloading img: "{img.url}"')

			if not overwrite:
				if img.local:
					log(f'\t\tSKIPPED (saved path) {f_path}')
					continue
				elif f_path.is_file():
					log(f'\t\tSKIPPED (exists on FS) {f_path}')
					img.local = f_path.relative_to(CACHE_DIR)
					continue

			res = requests.get(img.url)
			assert res.status_code == 200
			log(f'\t\t{len(res.content)}bytes -> {f_path}')
			f_path.write_bytes(res.content)
			img.local = f_path.relative_to(CACHE_DIR)
			cls.set_file_date(f_path, img.date)
		
		if auto_dump:
			cls.dump()


p = ApodProvider
# p.load()
