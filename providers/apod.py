#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, date as Date
from typing import Optional, Union
from pathlib import Path

import requests
import lxml.html
from lxml.html import HtmlElement
from singleton_decorator import singleton

from .base import ImageBase, ProviderBase, StatusEnum, CACHE_DIR, log


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

from enum import Enum

class ApodStatus(StatusEnum, Enum):

	# the layout is vertical, so the image is in portrait mode
	HORIZONTAL = 'HORIZONTAL'
	# the layout is old, so the image is probably very small and
	# it don't matter to us
	OLD = 'OLD'

	# Pages without static images (videos, applets, interactive stuff, etc)
	IFRAME = 'IFRAME'
	OBJECT = 'OBJECT'
	EMBED = 'EMBED'
	APPLET = 'APPLET'


PageStatus = ApodStatus


@dataclass
class ApodImage(ImageBase):
	# date: str
	# f_name: str
	# url: str
	...


##### PROVIDER CLASS #####

@singleton
class ApodProvider(ProviderBase):
	SHORT_NAME = 'apod'

	# For pylint sakes
	# DATA_DIR: ClassVar[Path]
	# IMG_DIR: ClassVar[Path]
	# DATA_FILE: ClassVar[Path]
	# data: ClassVar[list[ImageBase]]

	@property
	def PAGE_DIR(self) -> Path:
		return self.DATA_DIR / 'pages'
	# PAGE_DIR: Path = DATA_DIR / 'pages'

	# ARCHIVE_URL = "https://apod.nasa.gov/apod/archivepix.html"
	# FULL_ARCHIVE_URL = "https://apod.nasa.gov/apod/archivepixFull.html"
	# DATE_URL_BASE = "https://apod.nasa.gov/apod/ap%y%m%d.html"
	# DATE_FNAME_BASE = 'ap%y%m%d.html'

	URL_BASE = "https://apod.nasa.gov/apod/"
	DATE_F_NAME_BASE = 'ap%y%m%d.html'
	ARCHIVE_F_NAME = "archivepix.html"
	FULL_ARCHIVE_F_NAME = "archivepixFull.html"


	@classmethod
	def date2page_name(cls, date: Date) -> str:
		return date.strftime(cls.DATE_F_NAME_BASE)

	@classmethod
	def page_name2date(cls, page_name: str) -> Date:
		return datetime.strptime(page_name, cls.DATE_F_NAME_BASE).date()


	def get_page(self, f_name: str, cache=PAGE_DIR) -> str:
		log(f"{self.__class__.__name__}: Getting page ({f_name=})")

		# f_name = date.strftime(self.DATE_FNAME_BASE)

		if cache and (cache / f_name).is_file():
			page = (cache / f_name).read_text(errors='replace')
		else:
			page = self.download_day_page(date)

		return page


	def get_day_info(self, date: Date, cache=PAGE_DIR):
		log(f"{self.__class__.__name__}: Getting day info ({date=})")

		f_name = self.date2page_name(date)
		page = self.download_day_page(date, cache)
		return self.parse_day_page(page, date, f_name)

	
	def get_archive_info(self, full_archive=False, cache:Optional[Path]=None):
		log(f"{self.__class__.__name__}: Getting archive info ({full_archive=})")

		f_name = 'archivepix.html' if not full_archive else 'archivepixFull.html'

		if cache and (cache / f_name).is_file():
			page = (cache / f_name).read_text(errors='replace')
		else:
			page = self.download_archive_page(full_archive)

		return self.parse_archive_page(page)

	def get_pages_list(self, cache=None, full:bool=False) -> list[str]:
		if cache is True:
			cache = self.DATA_DIR
		return self.get_archive_info(full, cache)


	# TODO: unify all download functions

	def download_day_page(self, date: Date, save_cache=True) -> str:
		return self.download_page(self.date2page_name(date), save_cache)

	def download_archive_page(self, full_archive=False, save_cache=True) -> str:
		f_name = self.FULL_ARCHIVE_F_NAME if full_archive else self.ARCHIVE_F_NAME
		return self.download_page(f_name, save_cache)

	def download_page(self, f_name:str, save_cache=True) -> str:
		log(f"{self.__class__.__name__}: Downloading page ({f_name=})")
	
		url = self.URL_BASE + f_name
		res = requests.get(url)
		assert res.status_code == 200

		if save_cache:
			if save_cache is True:
				save_cache = self.PAGE_DIR
			assert isinstance(save_cache, Path)
			f_path = save_cache / f_name
			log(f"{self.__class__.__name__}: \tSaving archive (file={f_path})")
			f_path.write_bytes(res.content)
		
		return res.text

	# @classmethod
	# def download_day_page(cls, date: Date, cache=PAGE_DIR, save_raw=True) -> str:
	# 	log(f"{self.__class__.__name__}: Downloading day pages ({date=})")
	
	# 	f_name = cls.date2page_name(date)
	# 	url = cls.URL_BASE + f_name
	# 	res = requests.get(url)
	# 	assert res.status_code == 200

	# 	if save_raw:
	# 		f_path = cache / f_name
	# 		log(f"{self.__class__.__name__}: \tSaving arquive (file={f_path})")
	# 		f_path.write_bytes(res.content)
		
	# 	return res.text

	# @classmethod
	# def download_archive_page(cls, full_archive=False, save_raw=True) -> str:
	# 	log(f"{self.__class__.__name__}: Downloading archive info ({full_archive=})")

	# 	f_name = cls.FULL_ARCHIVE_F_NAME if full_archive else cls.ARCHIVE_F_NAME
	# 	url = cls.URL_BASE = f_name
	# 	res = requests.get(url)
	# 	assert res.status_code == 200

	# 	if save_raw:
	# 		f_path = cls.DATA_DIR / f_name
	# 		log(f"{self.__class__.__name__}: \tSaving arquive (file={f_path})")
	# 		f_path.write_bytes(res.content)
		
	# 	return res.text

	def parse_archive_page(self, page: str) -> list[str]:
		dom = get_dom(page)
		entries = dom.xpath('/html/body/b/a/@href')
		pages = list(map(str, entries))
		return pages

	def parse_day_page(self, page: str, date: Date, f_name:str):
		dom = get_dom(page)

		if n_img := self._should_skip_page(dom):
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

	@staticmethod
	def _should_skip_page(dom: HtmlElement) -> Union[bool, PageStatus]:
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


	def process_image_info(self, info: dict) -> ApodImage:
		return ApodImage(
			# date = info['startdate'],
			# title = info['title'],
			# about = info['copyright'],
			# _hash = info['hsh'],
			# url_path = info['url'],
			# url = self.BASE_IMG_URL + info['url'],
			# f_name = f_name,
			# extension = ext,
			# id_str = id_str,
			# id_num = id_num,
			# resolution = res,
		)

	def download_images(self, overwrite: bool = False, auto_dump: bool = True):
		log(f"{self.__class__.__name__}: Downloading images")
		for img in self.data:
			f_path = self.IMG_DIR / img.f_name
			log(f'{self.__class__.__name__}:\tDownloading img: "{img.url}"')

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
			self.set_file_date(f_path, img.date)
		
		if auto_dump:
			self.dump()


	def classify_pages(self, pages: list[str]) -> dict[str, PageStatus]:
		status = {}

		print()
		for page in pages:
			page_path: Path = self.PAGE_DIR / page

		print()
		return status


p = ApodProvider()
# p.load()

# for page in pages[:0]:
# 	pp = ApodProvider.PAGE_DIR / page
# 	t = pp.read_text(errors='replace')
# 	# try:
# 	if True:
# 		r = ApodProvider.parse_day_page(t, None, page)
# 		STATUS[page] = PageStatus.ERROR


def db_status_fill():
	from db import db, ApodStatus

	db.drop_tables([ApodStatus])
	db.create_tables([ApodStatus])

	from datetime import datetime
	with db.atomic():
		print()
		for page_name, status in reversed(STATUS.items()):
			print(f'***Inserting into db page {page_name}', end='\r')
			d = ApodProvider.page_name2date(page_name)
			ApodStatus.create(date=d, f_name=page_name, status=status.name, status_int=status.value)
		print('Done')
	db.commit()




import yaml
pages = yaml.unsafe_load(open('cache/apod/pages_list.yaml'))
pages.reverse()

_STATUS_FILE = p.DATA_DIR / 'STATUS.yaml'
_GROUPS_FILE = p.DATA_DIR / 'GROUPS.yaml'
# sSTATUS = yaml.unsafe_load(_STATUS_FILE.open())
# GROUPS = yaml.unsafe_load(_GROUPS_FILE.open())

STATUS = {}
pages.reverse()

# for page in pages[:0]:
# 	print(f'processing {page}', end='\t')
# 	pp = p.PAGE_DIR / page
# 	t = pp.read_text(errors='replace')
# 	# try:
# 	if True:
# 		r = p.parse_day_page(t, None, page)
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
