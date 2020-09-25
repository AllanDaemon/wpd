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
	status = CharField(choices=['UNPROCESSED', 'OK', 'VERTICAL', 'OLD', 'IFRAME', 'OBJECT', 'EMBED', 'APPLET', 'ERROR'])
	status_int = IntegerField(choices=[0, 1, 2, 3, 10, 11, 12, 13, 100])

assert db.connect()

