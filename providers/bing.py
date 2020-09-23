#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from typing import Optional
from pathlib import Path
import yaml
import re
import os

import requests

from .base import ImageBase, ProviderBase, CACHE_DIR, log


@dataclass
class BingImage(ImageBase):
	date: str
	title: str
	about: str
	url: str
	url_path: str
	f_name: str
	extension: str
	id_str: str
	id_num: int
	resolution: tuple[int, int]
	_hash: str
	local: Optional[Path] = None



class BingProvider(ProviderBase):
	SHORT_NAME = 'bing'

	BASE_IMG_URL = "http://bing.com"
	BASE_URL = "http://www.bing.com/HPImageArchive.aspx"
	BASE_PARAMS = {
		'format': 'js',
		'idx': 0,
		'n': 100,
		'mkt': 'en-US'
	}

	# DATA_DIR = CACHE_DIR / SHORT_NAME
	# IMG_DIR = DATA_DIR / 'imgs'
	# DATA_FILE = DATA_DIR / f'{SHORT_NAME}.yaml'

	data: list[BingImage]

	@classmethod
	def download(cls):
		cls.data = cls.download_info()
		cls.dump()

	@classmethod
	def download_info(cls, save_raw=True):
		log(f"{cls.__name__}: Downloading info")
		params = cls.BASE_PARAMS
		res = requests.get(cls.BASE_URL, params=params)
		assert res.status_code == 200
		if save_raw:
			now = datetime.now().strftime("%Y%m%d_%H%M%S")
			f_path = cls.DATA_DIR / 'raw' / f'bing_{now}.json'
			log(f"{cls.__name__}: \tSaving info (file={f_path})")
			f_path.write_bytes(res.content)

		imgs_raw = res.json()['images']
		imgs = list(map(cls.process_image_info, imgs_raw))
		return imgs

	@classmethod
	def process_image_info(cls, info: dict) -> BingImage:
		f_name, id_str, id_num, ext, res = url_extract_info(info['url'])
		return BingImage(
			date = info['startdate'],
			title = info['title'],
			about = info['copyright'],
			_hash = info['hsh'],
			url_path = info['url'],
			url = cls.BASE_IMG_URL + info['url'],
			f_name = f_name,
			extension = ext,
			id_str = id_str,
			id_num = id_num,
			resolution = res,
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
			set_file_date(f_path, img.date)
		
		if auto_dump:
			cls.dump()


	@classmethod
	def dump(cls):
		log(f"{cls.__name__}: Dumping data (file={cls.DATA_FILE})")
		yaml.dump(cls.data, cls.DATA_FILE.open('w'))

	@classmethod
	def load(cls):
		log(f"{cls.__name__}: Loading data (file={cls.DATA_FILE})")
		cls.data = yaml.unsafe_load(cls.DATA_FILE.open())



_ID_PATTERN = re.compile(r'OHR\.([^_]+)_EN-US(\d*)_(\d+)x(\d+).(\w+)', re.I | re.U)

def url_extract_info(url: str) -> tuple[str, str, int, str, tuple[int, int]]:
	query = urlparse(url).query
	_id = parse_qs(query)['id'][0]
	m = _ID_PATTERN.match(_id)
	assert m and len(m.groups()) == 5
	id_str, _id_n, _r_w, _r_h, ext = m.groups()
	id_n = int(_id_n)
	r_w = int(_r_w)
	r_h = int(_r_h)
	return _id, id_str, id_n, ext, (r_w, r_h)

def set_file_date(f: Path, date: str):
	a_time = f.stat().st_mtime
	m_time = datetime.strptime(date, '%Y%m%d').timestamp()
	os.utime(f, (a_time, m_time))



p = BingProvider
# p.load()
