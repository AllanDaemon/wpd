#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from pathlib import Path
import re

import requests

from .base import ImageBase, ProviderBase, CACHE_DIR, log


##### IMAGE DATA #####

@dataclass
class BingImage(ImageBase):
	# date: str
	# f_name: str
	# url: str
	title: str
	about: str
	url_path: str
	extension: str
	id_str: str
	id_num: int
	_resolution: tuple[int, int]
	_hash: str

	@property
	def _match_res(self):
		return self.resolution == self._resolution


##### PROVIDER CLASS #####

class BingProvider(ProviderBase):
	SHORT_NAME = 'bing'

	DATA_DIR = CACHE_DIR / SHORT_NAME
	IMG_DIR = DATA_DIR / 'imgs'
	DATA_FILE = DATA_DIR / f'{SHORT_NAME}.yaml'

	data: list[BingImage]

	BASE_URL = "http://www.bing.com/HPImageArchive.aspx"
	BASE_IMG_URL = "http://bing.com"
	BASE_PARAMS = {
		'format': 'js',
		'idx': 0,
		'n': 100,
		'mkt': 'en-US'
	}

	def download(self, idx=0):
		if not self.data:
			self.data = []
		self.data += self.download_info(idx)
		self.dump()

	def download_info(self, idx=0, save_raw=True):
		log(f"{type(self).__name__}: Downloading info")
		params = self.BASE_PARAMS
		params['idx'] = idx
		res = requests.get(self.BASE_URL, params=params)
		assert res.status_code == 200
		if save_raw:
			now = datetime.now().strftime("%Y%m%d_%H%M%S")
			f_path = self.DATA_DIR / 'raw' / f'bing_{now}.json'
			log(f"{type(self).__name__}: \tSaving info (file={f_path})")
			f_path.write_bytes(res.content)

		imgs_raw = res.json()['images']
		imgs = list(map(self.process_image_info, imgs_raw))
		return imgs

	def process_image_info(self, info: dict) -> BingImage:
		f_name, id_str, id_num, ext, res = url_extract_info(info['url'])
		return BingImage(
			date = info['startdate'],
			title = info['title'],
			about = info['copyright'],
			_hash = info['hsh'],
			url_path = info['url'],
			url = self.BASE_IMG_URL + info['url'],
			f_name = f_name,
			extension = ext,
			id_str = id_str,
			id_num = id_num,
			_resolution = res,
		)

	# TODO: REMOVE
	def download_images(self, overwrite: bool = False, auto_dump: bool = True):
		log(f"{type(self).__name__}: Downloading images")
		for img in self.data:
			f_path = self.IMG_DIR / img.f_name
			log(f'{type(self).__name__}:\tDownloading img: "{img.url}"')

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
			self.set_file_date(f_path, self.to_datetime(img.date))
		
		if auto_dump:
			self.dump()



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


if __name__ == "__main__":
	p = BingProvider()
	p.load()
