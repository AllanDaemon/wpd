#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from collections import UserList
import yaml
import re

import requests

from base import ImageBase, ProviderBase, CACHE_DIR, log


BING_CACHE_DATA = CACHE_DIR / 'bing'
BING_CACHE_IMG = BING_CACHE_DATA / 'imgs'


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


_ID_PATTERN = re.compile(r'OHR\.([^_]+)_EN-US(\d*)_(\d+)x(\d+).(\w+)', re.I | re.U)

def url_extract_info(url: str) -> tuple[str, str, int, str, tuple[int, int]]:
	query = urlparse(url).query
	_id = parse_qs(query)['id'][0]
	m = _ID_PATTERN.match(_id)
	assert m
	groups = m.groups()
	assert len(groups) == 5
	id_str, _id_n, _r_w, _r_h, ext = groups
	id_n = int(_id_n)
	r_w = int(_r_w)
	r_h = int(_r_h)
	assert isinstance(id_str, str)
	assert isinstance(id_n, int)
	return _id, id_str, id_n, ext, (r_w, r_h)


class BingProvider(ProviderBase, UserList):
	BASE_IMG_URL = "http://bing.com"
	BASE_URL = "http://www.bing.com/HPImageArchive.aspx"
	BASE_PARAMS = {
		'format': 'js',
		'idx': 0,
		'n': 100,
		'mkt': 'en-US'
	}

	DATA_FILE = BING_CACHE_DATA / f'bing.yaml'

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
			f_path = BING_CACHE_DATA / 'raw' / f'bing_{now}.json'
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
	def download_images(cls):
		log(f"{cls.__name__}: Downloading images")
		...

	@classmethod
	def dump(cls):
		log(f"{cls.__name__}: Dumping data (file={cls.DATA_FILE})")
		yaml.dump(cls.data, cls.DATA_FILE.open('w'))

	@classmethod
	def load(cls):
		log(f"{cls.__name__}: Loading data (file={cls.DATA_FILE})")
		cls.data = yaml.unsafe_load(cls.DATA_FILE.open())



p = BingProvider
# p.load()
