#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Text, DateTime
from iflychatbot.models.shared import Base

class Site(Base):
	__tablename__ = 'site'
	id = Column('id', Integer, primary_key=True)
	name = Column('name', String(256))
	ifc_room_id = Column('ifc_room_id', Integer)
	ifc_key = Column('ifc_key', String(512))

	def __init__(self): 
		self.users = []
		self.available_users = []
	
	def __repr__(self):
		return "{} [ id: {}, room_id: {}, iFC_Key: {} ]"\
		.format(self.name, self.id, self.ifc_room_id, self.ifc_key[:8])

class User(Base):
	__tablename__ = 'user'
	id = Column('id', Integer, primary_key=True)
	name = Column('name', String(256))
	active = Column('active', Integer)
	source_id = Column('source_id', Integer)
	source_name = Column('source_name', String(256))
	image = Column('image', String(2048))

	def __init__(self):
		self.source = None

	def __repr__(self):
		return "{} [ id: {}, active: {}, source_id: {}, image: {} ]"\
		.format(self.name, self.id, self.active, self.source_id, self.image[:10] + '...')

class Site_User(Base):
	__tablename__ = 'site_user'
	id = Column('id', Integer, primary_key=True)
	site_id = Column('site_id',Integer)
	user_id = Column('user_id', Integer)

	def __init__(self): pass
	
	def __repr__(self):
		return "[ id: {}, site_id: {}, user_id: {} ]"\
		.format(self.id, self.site_id, self.user_id)

class Source(Base):
	__tablename__ = 'source'
	id = Column('id', Integer, primary_key=True)
	name = Column('name', String(256))
	id_str = Column('id_str', String(64))
	profile_image_url = Column('profile_image_url', String(2048))
	created_at = Column('created_at', DateTime)
	updated_at = Column('updated_at', DateTime)

	def __init__(self):
		tweets = []

	def __repr__(self):
		return "{} [ id: {}, id_str: {}, created_at: {}, updated_at: {} ]"\
		.format(self.name, self.id, self.id_str, self.created_at, self.updated_at)

class Source_Tweet(Base):
	__tablename__ = 'source_tweet'
	id = Column('id', Integer, primary_key=True)
	source_id = Column('source_id', Integer)
	id_str = Column('id_str', String(64))
	screen_name = Column('screen_name', String(256))
	text = Column('text', String(1024))
	created_at = Column('created_at', DateTime)
	raw = Column('raw', Text)

	def __init__(self): pass

	def __repr__(self):
		return "{}: {} [ {}: text: {} ]"\
		.format(self.id, self.screen_name, self.created_at, self.text.encode('utf-8'))


class Reader(Base):
	__tablename__ = 'reader'
	id = Column('id', Integer, primary_key=True)
	name = Column('name', String(256))
	password = Column('password', String(256))
	credentials = Column('credentials', String(8192))

	def __init__(self): pass

	def __repr__(self):
		return "Reader: {}\n\tId: {}\n\tPassword: {}\n\tCredentials: {}"\
		.format(self.name, self.id, self.password, self.credentials)

class IFC_Message(Base):
	__tablename__ = 'ifc_message'
	id = Column('id', Integer, primary_key=True)

	site_id = Column('site_id', Integer)
	user_id = Column('user_id', Integer)
	source_tweet_id = Column('source_tweet_id', Integer)

	room_id = Column('room_id', String(16))
	from_id = Column('from_id', String(32))
	from_name = Column('from_name', String(64))
	picture_url = Column('picture_url', String(2048))
	profile_url = Column('profile_url', String(256))
	message_id = Column('message_id', String(512))
	message = Column('message', String(1024))
	
	posted = Column('posted', Integer)
	type = Column('type', String(32))
	status = Column('status', String(32))
	timer = Column('timer', Integer)

	created_on = Column('created_on', String(128))

	def __init__(self): 
		self.site_name = ''

	def __repr__(self):
		return "RoomId: {}\nName: {}\nMessage: {}\nPosted: {}\n---"\
		.format(self.room_id, self.from_name, self.message, self.posted)



