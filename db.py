#!/usr/bin/env python3

from __future__ import annotations
from os import stat

from peewee import CharField, DateField, IntegerField, Model, SqliteDatabase

db = SqliteDatabase('cache/wpd.db')


class BaseModel(Model):
	class Meta:
		database = db


class ApodStatus(BaseModel):
	date = DateField(primary_key=True)
	f_name = CharField(unique=True)
	status = CharField(choices=['UNPROCESSED', 'OK', 'VERTICAL', 'IFRAME', 'OBJECT', 'EMBED', 'APPLET', 'ERROR'])
	status_int = IntegerField(choices=[0, 1, 2, 10, 11, 12, 13, 100])



assert db.connect()
db.drop_tables([ApodStatus])
db.create_tables([ApodStatus])

from datetime import datetime
from providers.apod import STATUS, Status, ApodProvider


with db.atomic():
	print()
	for page_name, status in reversed(STATUS.items()):
		print(f'***Inserting into db page {page_name}', end='\r')
		d = datetime.strptime(page_name, ApodProvider.DATE_FNAME_BASE).date()
		# rows.append(dict(date=d, f_name=page_name, status=status.name, status_int=status.value))
		ApodStatus.create(date=d, f_name=page_name, status=status.name, status_int=status.value)
	print('Done')


db.commit()

