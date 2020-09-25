#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
from datetime import date as Date
from typing import Union, ClassVar
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

from enum import IntEnum

class PageStatus(IntEnum):
	UNPROCESSED = 0
	OK = 1

	# the layout is vertical, so the image is in portrait mode
	HORIZONTAL = 2
	# the layout is old, so the image is probably very small and
	# it don't matter to us
	OLD = 3

	# Pages without static images (videos, applets, interactive stuff, etc)
	IFRAME = 10
	OBJECT = 11
	EMBED = 12
	APPLET = 13

	# General errors when handling the page
	ERROR = 100


@dataclass
class ApodImage(ImageBase):
	# date: str
	# f_name: str
	# url: str
	...


##### PROVIDER CLASS #####

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
	def get_archive_info(cls, full_archive=False, cache=PAGE_DIR):
		log(f"{cls.__name__}: Getting day info ({date=})")

		f_name = date.strftime(cls.DATE_FNAME_BASE)

		if cache and (cache / f_name).is_file():
			page = (cache / f_name).read_text(errors='replace')
		else:
			page = cls.download_day_page(date)

		return cls.parse_day_page(page, date, f_name)

	# TODO: unify all download functions
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
	def download_archive_info(cls, full_archive=False, save_raw=True) -> str:
		log(f"{cls.__name__}: Downloading archive info ({full_archive=})")

		url = cls.ARCHIVE_URL if not full_archive else cls.FULL_ARCHIVE_URL
		res = requests.get(url)
		assert res.status_code == 200

		if save_raw:
			_f_name = Path(url)
			f_path = cls.DATA_DIR / _f_name.name
			log(f"{cls.__name__}: \tSaving arquive (file={f_path})")
			f_path.write_bytes(res.content)
		
		return res.text

	@classmethod
	def parse_day_page(cls, page: str, date: Date, f_name:str):
		dom = get_dom(page)

		is_layout_horizontal = not dom.xpath('/html/body/table')

		if n_img := cls._should_skip_page(dom):
			return n_img

		image_href = dom.css_one('body > center:first-child > p:last-child > a').attrib['href']

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

		return PageStatus.OK
		return image_href, title, credit, explanation

	@classmethod
	def _should_skip_page(cls, dom: HtmlElement) -> Union[bool, PageStatus]:
		# Old page format, we don't proccess them because the
		# images are too small for being used as wallpaper.
		if not dom.cssselect('body > center'):
			return PageStatus.OLD

		# Pages with horizontal layout means image in portrait
		# mode, so we don't want them.
		if dom.xpath('/html/body/table'):
			return PageStatus.HORIZONTAL

		link_node: HtmlElement = dom.css_one('body > center:first-child > p:last-child')
		if link_node.cssselect('iframe'):
			return PageStatus.IFRAME
		if link_node.cssselect('object'):
			return PageStatus.OBJECT
		if link_node.cssselect('embed'):
			return PageStatus.EMBED
		if link_node.cssselect('applet'):
			return PageStatus.APPLET
		return False


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




def db_status_fill():
	from db import db, ApodStatus

	db.drop_tables([ApodStatus])
	db.create_tables([ApodStatus])

	from datetime import datetime
	with db.atomic():
		print()
		for page_name, status in reversed(STATUS.items()):
			print(f'***Inserting into db page {page_name}', end='\r')
			d = datetime.strptime(page_name, ApodProvider.DATE_FNAME_BASE).date()
			ApodStatus.create(date=d, f_name=page_name, status=status.name, status_int=status.value)
		print('Done')
	db.commit()


p = ApodProvider
# p.load()

import yaml
pages = yaml.unsafe_load(open('cache/apod/pages_list.yaml'))
pages.reverse()

_STATUS_FILE = ApodProvider.DATA_DIR / 'STATUS.yaml'
_GROUPS_FILE = ApodProvider.DATA_DIR / 'GROUPS.yaml'
# sSTATUS = yaml.unsafe_load(_STATUS_FILE.open())
# GROUPS = yaml.unsafe_load(_GROUPS_FILE.open())

STATUS = {}
pages.reverse()

# for page in pages[:0]:
# 	print(f'processing {page}', end='\t')
# 	pp = ApodProvider.PAGE_DIR / page
# 	t = pp.read_text(errors='replace')
# 	# try:
# 	if True:
# 		r = ApodProvider.parse_day_page(t, None, page)
# 		STATUS[page] = PageStatus.ERROR



# _group = PageStatus.ERROR.name
# for page in GROUPS[_group]:
# 	print(f'processing {_group=} {page=}', end='\t')
# 	pp = ApodProvider.PAGE_DIR / page
# 	t = pp.read_text(errors='replace')
# 	dom = get_dom(t)
# 	is_old_format = not dom.cssselect('body > center')
# 	print('OLD' if is_old_format else 'NORMAL')
# 	# assert is_old_format
