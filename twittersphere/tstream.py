#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import threading
sys.path.append('/home/twitterbot/public_html/iflychatbot/')
import atexit
reload(sys)
sys.setdefaultencoding('utf-8')
import time
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from tweepy import API
import json
from datetime import datetime
import requests

from iflychatbot.models.shared import db
from iflychatbot.models.dbmodels import *

from colorama import init, Fore
init()


class TwitterSphere(StreamListener):
	def __init__(self):
		self.time_started = datetime.now()
		pass

	def run(self):
		global twitter_user_ids
		global twitter_screen_names
		global running
		global update_stream
		while running:
			try:
	#			print(''twitter_user_ids)

				if update_stream: #start/update
					twitterStream.disconnect()
					twitterStream.filter(follow=twitter_user_ids, async=True)
					print('\nStream started')
					print('\nTracking: ')
					print(twitter_screen_names)
					update_stream  = False
			except Exception,e:
				print('\nTwitterSphere error...\n' + str(e))
				update_stream = True
				pass

			time.sleep(15)
			c_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			time_running = datetime.now() - self.time_started

	def on_status(self, status):
		print(status.text)

	def on_data(self, data):
		global update_stream
		try:
				all_data = json.loads(data)
				try:
					tweet = all_data["text"]
					username = all_data["user"]["screen_name"].lower()
					id_str = all_data["user"]["id_str"]
					created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(all_data['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))

				except KeyError:
					print('\nTweet with no text: {0}'.format(str(all_data).encode('utf-8')))
					return True

				# Prevent duplicates
				exists = Source_Tweet.query.filter(Source_Tweet.text == tweet)
				if exists.count() != 0:
					print('Duplicate in on_data, from where?\n\t{}'.format(tweet.encode('utf-8')))
					return True

				stdb = Source_Tweet()
				stdb.id_str = id_str.encode('utf-8')
				stdb.screen_name = username.encode('utf-8')
				stdb.text = tweet.encode('utf-8')
				stdb.created_at = created_at
				stdb.raw = str(all_data).encode('utf-8')
				db.add(stdb)
				db.flush()

				if username in twitter_screen_names:
					tSource = Source.query.filter(Source.name == username).limit(1)[0]
					tUsers = User.query.filter(User.source_id == tSource.id, User.active == 1)
					for u in tUsers:
						#get sites
						su = Site_User.query.filter(Site_User.user_id == u.id)
						for su_ifc in su:
							site = Site.query.get(su_ifc.site_id)
							if site == None: continue
							m = IFC_Message()
							m.user_id = u.id
							m.site_id = site.id
							
							m.room_id = str(site.ifc_room_id)
							m.from_id = str(u.id)
							m.from_name = str(u.name)
							m.picture_url = str(u.image)
							m.profile_url = "javascript:void(0)"
#							m.message_id = str(j['message_id']).encode('utf-8')
							m.message = tweet.encode('utf-8')
							m.posted = 0
							m.created_on = str(created_at)
							m.source_tweet_id = stdb.id
							db.add(m)
							db.flush()
							print('\nSaved to ifc_message: ')
							print(m)
#							response = requests.get('http://192.169.141.201/iflychatbot/api/newmsg/{}/'.format(m.id))

					
					# check users with this twitterer as their source
					# check which sites the user is posting to and if the user is active
					# add ifc_message record with posted-flag to 0.
					# notify iflychatbot api of the new record (with ifc_message.id parameter)
					# post via the same method as in omnieye
					tweet_color = Fore.GREEN

					print('\n[{}] [Local: {}] User: {}\n\t{}\n'.format(datetime.now().strftime('%H:%M:%S'),
													created_at,
													Fore.CYAN+ username + Fore.RESET, 
													tweet_color + tweet + Fore.RESET))


				else:
					if "retweeted_status" in all_data:
						retweeted_status = all_data["retweeted_status"]
						tweet_color = Fore.YELLOW
					elif "in_reply_to_status_id_str" in all_data:
						is_reply = all_data["in_reply_to_status_id_str"]
						if not is_reply == None:
							tweet_color = Fore.YELLOW
						else:
							tweet_color = Fore.RED				  
					else:
						tweet_color = Fore.RED

				sys.stdout.write(Fore.MAGENTA + '.' + Fore.RESET)
				sys.stdout.flush()
		
		#
				return True
		except Exception,e:
			print('Exception in TwitterSphere:' + str(e))
			update_stream = True
			pass
	

	def on_error(self, status):
		print(status)

class TwitterSphereConfig:
	def __init__(self):
		print('TwitterSphereConfig...')
		#consumer key, consumer secret, access token, access secret.
		ckey="QpBbAaG5j5LQwtISpXHSnMaaZ"
		csecret="siWbAxNBq9KojlwcoTnmZqo6yrUNsWAvVhZZ9DOY9nP2wRIUiw"
		atoken="2728509485-FJjALLzmjoF4uBWMCWRz7gG2suUGSK9qYQiYI2a"
		asecret="eJe1olMUVhK5gxz2RNZYNd4RT5H0zrJmINg2ot8w07Jaw"

		api_url = 'http://192.169.141.201/iflychatbot/api/'

		self.users = User.query.all()
		self.sources = Source.query.all()
		self.sources_count = len(self.sources)
		self.sources_screen_names = [s.name.lower() for s in self.sources]

		# Provide Twitter Dev tokens
		auth = OAuthHandler(ckey, csecret)
		auth.set_access_token(atoken, asecret)

		# Use API to lookup id's for screen_names`
		self.api = API(auth)
		global twitterStream
		twitterStream = Stream(auth, TwitterSphere())
		global twitter_user_ids #keep this updated
		global twitter_screen_names
		twitter_user_ids = [s.id_str for s in self.sources	if s.id_str != None]
		twitter_screen_names = [s.name.lower() for s in self.sources if s.id_str != None]
		global update_stream
		update_stream = True #to trigger initial streaming, set false after stream starts


	def run(self):
		global running
		global update_stream
		while running:
			try:
				c_sources = Source.query.all()
				if self.sources_count != len(c_sources) or len([s.id for s in c_sources if s.id_str == None]) > 0:
					print('\nSources modified')
					self.sources = c_sources
					self.fetch_missing_ids()
					self.sources_count = len(self.sources)
					update_stream = True
				
				else:
					pass
			except Exception,e:
				print('\nTwitterSphereConfig error...\n' + str(e))
				update_stream = True
				pass
				
			time.sleep(10)

	def fetch_missing_ids(self):
		#Twitternames wihout known id's
		swoid = [s.name for s in self.sources if s.id_str == None]
		if len(swoid) == 0: return
		user_lookups = self.api.lookup_users(screen_names=swoid)
#		print('user_lookups response:\n{}'.format(user_lookups))

		user_ids = dict([(u.screen_name, u.id_str) for u in user_lookups])
		for k,v in user_ids.items():
			sdb_id = [s.id for s in self.sources if s.name == k.lower()]
			print('\nSource Id: {}'.format(sdb_id))
			sdb = Source.query.get(sdb_id)
			sdb.id_str = v
			print('\nUpdated: {} with twitter_id: {}{}{}'.format(k, Fore.GREEN, v, Fore.RESET).encode("utf8"))
		#Store to DB
		db.flush()
		#update twitter_user_ids array

		# Refresh id's and screen_names globally
		db.expire_all()
		self.sources = Source.query.all()
		global twitter_user_ids
		global twitter_screen_names
		twitter_user_ids = [s.id_str for s in self.sources if s.id_str != None]
		twitter_screen_names = [s.name.lower() for s in self.sources if s.id_str != None]

class IFlyPoster:
	def __init__(self):
		print('IFlyPoster...')
		self.timer = 5
		self.publish_url = "https://api.iflychat.com/api/1.1/room/{}/publish"
		self.repeattimer = 0

		
	def run(self):
		global running
		while running:
			try:
				queue = IFC_Message.query.filter(IFC_Message.posted == 0)
				for q in queue:
					self.postMessage(q)
				if self.repeattimer <= 0:
					repeat_messages = IFC_Message.query.filter(IFC_Message.type == 'repeat', IFC_Message.status == 'active')
					for m in repeat_messages:
						self.postMessage(m)
					self.repeattimer = 300
			
				
			except Exception,e:
				print('\nError in IFlyChatPoster..\n' + str(e))
				pass
			time.sleep(self.timer)
			self.repeattimer = self.repeattimer - self.timer

	def postMessage(self, ifc_message):
		try:
			if ifc_message.site_id == None: return
			site = Site.query.get(ifc_message.site_id)
			# Filter out retweets or urls
			# C#
			# if (text.IndexOf("@") == 0 || text.IndexOf("RT") == 0) return string.Empty;
			# if (text.LastIndexOf("http") != -1)
			#	 text = text.Substring(0, text.LastIndexOf("http"));
			if '@' in ifc_message.message or 'RT' in ifc_message.message:
				ifc_message.posted = 1
				db.flush()
				print('Skipped filtered message:\n{}'.format(ifc_message))
				return
			if 'http' in ifc_message.message:
				message = ifc_message.message[:ifc_message.message.index('http')]
			else:
				message = ifc_message.message
			r = requests.post(self.publish_url.format(site.ifc_room_id), 
				data = { 
					'api_key': site.ifc_key,
					'uid': ifc_message.from_id,
					'name': ifc_message.from_name,
					'picture_url': ifc_message.picture_url,
					'profile_url': 'javascript:void(0)',
					'message': message,
					'color': '#222222',
					'roles[]': '0'
				})
			if r.ok == True:
				ifc_message.posted = 1
				db.flush()
				if ifc_message.type != 'repeat':
					print('\nIFlyPoster posted:')
					print(ifc_message)
			else:
				print(r)
				print('\nIFlyPoster failed posting:')
				print(ifc_message)

		except Exception,e:
			print('\nError in IFlyChatPoster.postMessage...\n' + str(e))
			pass


class IFlyReader:
	def __init__(self):
		print('IFlyReader...')
		#todo db-config
		self.api_url = "https://api.iflychat.com/api/1.1/threads/get"
		self.api_key = "Ff3bAAZyGtK09tos5ZfXZLEvRy_60nkFsVMhy79vvykW6831"
#		3 is stackedbids.com
#		self.room_ids = ['2','3','4','6','7']
		self.room_ids = ['2','4','6','7']
		#start_timestamp = ms
		#end_timestamp = ms
		self.limit = "5"

	def run(self):
		c = 0
		while running:
			try:
				r = self.getThreadHistory()
#				print('Thread history count: ' + str(len(r)))
				for j in r:
					exists = IFC_Message.query.filter(IFC_Message.message_id == j['message_id'])
					if exists.count() != 0:
#						print(str(c) + ': Message allready entered')
						c = c + 1
						continue
					m = IFC_Message()
					m.room_id = str(j['room_id']).encode('utf-8')
					m.from_id = str(j['from_id']).encode('utf-8')
					m.from_name = str(j['from_name']).encode('utf-8')
					m.picture_url = str(j['picture_url']).encode('utf-8')
					m.profile_url = str(j['profile_url']).encode('utf-8')
					m.message_id = str(j['message_id']).encode('utf-8')
					m.message = j['message'].encode('utf-8')
					m.posted = True
					m.created_on = str(j['time']).encode('utf-8')
					db.add(m)
					db.flush()
					print('\n')
					print(m)
			except Exception,e:
				print('\nError in iFlyChat reader..\n' + str(e))
				pass
			
			time.sleep(30)
	def getThreadHistory(self):
		try:
			r = requests.post(self.api_url, data = { 'api_key': self.api_key, 'room_id': self.room_ids, 'limit': self.limit })
			if r.ok == True:
#				print(Fore.GREEN + '.' + Fore.RESET)
				sys.stdout.write(Fore.GREEN + '.' + Fore.RESET)
				sys.stdout.flush()
				return r.json()
			else:
				sys.stdout.write(Fore.RED+ '.' + Fore.RESET)
				sys.stdout.flush()
		except Exception,e:
			print('\nError getting iFlyChat History...\n' + str(e) )
			pass
	

def tstream_cleanup():
	print('Performing cleanup...')

if __name__ == '__main__':
	running = True
	print('Running.. ')

	tsc = TwitterSphereConfig()
	ts = TwitterSphere()
	ifr = IFlyReader()
	ifp = IFlyPoster()

	tsc_t = threading.Thread(target=tsc.run, args=())
	ts_t = threading.Thread(target=ts.run, args=())
	ifr_t = threading.Thread(target=ifr.run, args=())
	ifp_t = threading.Thread(target=ifp.run, args=())

	tsc_t.start()
	ts_t.start()
	ifr_t.start()
	ifp_t.start()

	atexit.register(tstream_cleanup)
	

