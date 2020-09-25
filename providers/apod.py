#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass
from os import readv
from re import error
from urllib.parse import urlparse, parse_qs
from datetime import date as Date
from typing import ClassVar
from pathlib import Path

import requests
import lxml.html
from lxml.html import HtmlElement

from .base import ImageBase, ProviderBase, CACHE_DIR, log


##### HELPERS #####

def get_dom(page: str) -> HtmlElement:
	return lxml.html.fromstring(page)

def css_one(dom: HtmlElement, selector: str):
	r = dom.cssselect(selector)
	assert r
	assert len(r) == 1
	return r[0]

def xp_one(dom: HtmlElement, xp: str):
	r = dom.xpath(xp)
	assert r
	assert len(r) == 1
	return r[0]

HtmlElement.css_one = css_one
HtmlElement.xp_one = xp_one


##### IMAGE DATA #####

@dataclass
class ApodImage(ImageBase):
	# date: str
	# f_name: str
	# url: str
	...


##### PROVIDER CLASS #####

# from .apod_non_picture_dates import non_picture_dates
non_picture_dates: list[str] = []

new_non_picture_dates: list[str] = []

class ApodProvider(ProviderBase):
	SHORT_NAME = 'apod'

	# For pylint sakes
	DATA_DIR: ClassVar[Path]
	IMG_DIR: ClassVar[Path]
	DATA_FILE: ClassVar[Path]
	data: ClassVar[list[ImageBase]]

	@property
	@classmethod
	def PAGE_DIR(cls) -> Path:
		return cls.DATA_DIR / 'pages'
	# PAGE_DIR: ClassVar[Path] = DATA_DIR / 'pages'

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
			page = (cache / f_name).read_text(errors='replace')
		else:
			page = cls.download_day_page(date)

		return cls.parse_day_page(page, date, f_name)

	@classmethod
	def download_day_page(cls, date: Date, cache=PAGE_DIR, save_raw=True) -> str:
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
	def parse_day_page(cls, page: str, date: Date, f_name:str):
		dom = get_dom(page)

		is_layout_horizontal = not dom.xpath('/html/body/table')

		n_img = cls._is_page_not_image(dom)
		if n_img:
			return n_img

		if not is_layout_horizontal:
			return Status.VERTICAL

		# if cls._is_page_not_image(dom) or not is_layout_horizontal:
		# 	if f_name not in non_picture_dates:
		# 		print("NEW VIDEO FOUND:\t", f_name)
		# 		new_non_picture_dates.append(f_name)
		# 		for v in new_non_picture_dates:
		# 			print(f"\t'{v}',")
		# 	print('Skipping video page:', f_name)
		# 	return None


		image_href = dom.css_one('body > center:first-child > p:last-child > a').attrib['href']
		# if is_layout_horizontal:
		# else:
		# 	image_href = dom.xp_one('/html/body/table/tr/td[1]/a').attrib['href']

		# try:
		# 	title = dom.xp_one('/html/body/center[2]/b[1]/text()').strip()
		# except AssertionError:
		# 	title = dom.xp_one('/html/body/center[2]/i/b[1]/text()').strip()
		title = None

		# block = dom.xp_one('/html/body/center[2]').text_content().strip().split('\n')
		# assert block.pop(0).strip() == title
		# credit_header = dom.xp_one('/html/body/center[2]/b[2]/text()').strip()
		# credit = ' '.join(block).strip().removeprefix(credit_header).strip()
		credit = None

		# expl_header = dom.xp_one('/html/body/p[1]/b/text()').strip()
		# explanation = dom.xp_one('/html/body/p[1]').text_content().strip()
		# explanation = explanation.removeprefix(expl_header).strip()
		explanation = None

		return Status.OK
		return image_href, title, credit, explanation

	@classmethod
	def _is_page_not_image(cls, dom: HtmlElement) -> bool:
		link_node: HtmlElement = dom.css_one('body > center:first-child > p:last-child')
		iframe = link_node.cssselect('iframe')
		if iframe:
			assert len(iframe) == 1
			iframe = iframe[0]
			return Status.IFRAME
			src = iframe.attrib['src']
			if 'youtube.com' in src: return True
			elif 'vimeo.com' in src: return True
			elif 'ustream.tv' in src: return True
			elif 'meteorshowers.org' in src: return True
			elif 'apod.nasa.gov' in src: return True
			elif 'earth.nullschool.net' in src: return True
			elif 'sci.esa.int' in src: return True
			elif 'vestatrek.jpl.nasa.gov' in src: return True
			else:
				return True
				# breakpoint()
				# raise NotImplementedError

		# object_node = link_node.find_class('object')
		object_node = link_node.cssselect('object')
		if object_node:
			return Status.OBJECT
			# assert len(object_node) == 1
			# object_node = object_node[0]
			# _type = object_node.attrib['type']
			# if _type in (
			# 	'application/x-shockwave-flash',
			# ): return True
			# else:
			# 	breakpoint()
			# 	raise NotImplementedError

		embed = link_node.cssselect('embed')
		if embed:
			return Status.EMBED

		applet = link_node.cssselect('applet')
		if applet:
			return Status.APPLET

		return False



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


from enum import IntEnum

class Status(IntEnum):
	UNPROCESSED = 0
	OK = 1
	VERTICAL = 2
	IFRAME = 10
	OBJECT = 11
	EMBED = 12
	APPLET = 13
	ERROR = 100


import yaml
pages = yaml.unsafe_load(open('cache/apod/pages_list.yaml'))
pages.reverse()
PAGE_DIR = ApodProvider.DATA_DIR / 'pages'



# for page in pages[4000:]:
# 	if page in non_picture_dates:
# 		print('skipping video', page)
# 		continue
# 	print(f'processing {page}')
# 	pp = PAGE_DIR / page
# 	t = pp.read_text(errors='replace')
# 	r = ApodProvider.parse_day_page(t, None, page)
# 	if r:
# 		print('\t',r[0], r[1])
# 	else:
# 		print("NONE")


p = ApodProvider
# p.load()


STATUS = {}

for page in pages:
	print(f'processing {page}', end='\t')
	pp = PAGE_DIR / page
	t = pp.read_text(errors='replace')
	try:
		r = ApodProvider.parse_day_page(t, None, page)
		STATUS[page] = r
		if r:
			print('\t', r)
		else:
			print("\tNONE")
	except:
		print("\tERROR")
		STATUS[page] = Status.ERROR
