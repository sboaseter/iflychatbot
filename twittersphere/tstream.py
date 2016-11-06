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
#			print(''twitter_user_ids)

			if update_stream: #start/update
				twitterStream.disconnect()
				twitterStream.filter(follow=twitter_user_ids, async=True)
				print('Stream started')
				print('Tracking: ')
				print(twitter_screen_names)
				update_stream  = False
			
			time.sleep(15)
			c_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			time_running = datetime.now() - self.time_started
			print('{}\n=== TwitterSphere running[ {}s ] ===\n{}'.format(Fore.GREEN, time_running.total_seconds(), Fore.RESET))
#			c_sources = Source.query.all()
#			print(Fore.GREEN + '[Sources]:' + str(len(c_sources)) + Fore.RESET)

#			for cs in c_sources:
#				print('{}{}{} {}[{}]{}'.format(Fore.CYAN, cs.name, Fore.RESET,
#												Fore.YELLOW, cs.id_str, Fore.RESET))

	def on_status(self, status):
		print(status.text)

	def on_data(self, data):
		all_data = json.loads(data)
		try:
			tweet = all_data["text"]
			username = all_data["user"]["screen_name"].lower()
			id_str = all_data["user"]["id_str"]
			created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(all_data['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))

		except KeyError:
			print('Tweet with no text: {0}'.format(str(all_data).encode('utf-8')))
			return True
#		print(tweet.encode('utf-8'))
#		print('.', end="", flush=True)
#		sys.stdout.write('.')
#		sys.stdout.flush()

		stdb = Source_Tweet()
		stdb.id_str = id_str.encode('utf-8')
		stdb.screen_name = username.encode('utf-8')
		stdb.text = tweet.encode('utf-8')
		stdb.created_at = created_at
		stdb.raw = str(all_data).encode('utf-8')

		if username in twitter_screen_names:
			api_url = 'http://192.169.141.201/iflychatbot/api/'
			payload = {'screen_name': username.encode('utf-8'), 'tweet': tweet.encode('utf-8')}
			response = requests.post(api_url, json=payload)

			tweet_color = Fore.GREEN
			print('[{}] [Local: {}] User: {}\n\t{}\n'.format(datetime.now().strftime('%H:%M:%S'),
													created_at,
													Fore.CYAN+ username + Fore.RESET, 
													tweet_color + tweet + Fore.RESET))


#			username = '_screen_name_' + username
#			matched_source = [s.id for s in sources if s.name.lower() == username]
#			if len(matched_source) > 0:
#				stdb.source_id = matched_source[0]

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

		db.add(stdb)
		db.flush()
		
#
		return True

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
		twitter_user_ids = [s.id_str for s in self.sources  if s.id_str != None]
		twitter_screen_names = [s.name.lower() for s in self.sources if s.id_str != None]
		global update_stream
		update_stream = True #to trigger initial streaming, set false after stream starts


	def run(self):
		global running
		global update_stream
		while running:
#			c_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#			print('{}\n===Checking configuration [ {} ] ===\n{}'.format(Fore.GREEN, c_time, Fore.RESET))
			c_sources = Source.query.all()
			if self.sources_count != len(c_sources):
				print('Sources modified')
				self.sources = c_sources
				self.fetch_missing_ids()
				self.sources_count = len(self.sources)
				update_stream = True
				
			else:
				pass
				
#			print(Fore.GREEN + '[Sources]:' + str(len(c_sources)) + Fore.RESET)

#			for cs in c_sources:
#				print('{}{}{} {}[{}]{}'.format(Fore.CYAN, cs.name, Fore.RESET,
#												Fore.YELLOW, cs.id_str, Fore.RESET))

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
			print('Source Id: {}'.format(sdb_id))
			sdb = Source.query.get(sdb_id)
			sdb.id_str = v
			print('Updated: {} with twitter_id: {}{}{}'.format(k, Fore.GREEN, v, Fore.RESET).encode("utf8"))
		#Store to DB
		db.flush()
		#update twitter_user_ids array

		# Refresh id's and screen_names globally
		self.sources = Source.query.all()
		global twitter_user_ids
		global twitter_screen_names
		twitter_user_ids = [s.id_str for s in self.sources if s.id_str != None]
		twitter_screen_names = [s.name.lower() for s in self.sources if s.id_str != None]



class IFlyReader:
	def __init__(self):
		print('IFlyReader...')
		#todo db-config
		self.api_url = "https://api.iflychat.com/api/1.1/threads/get"
		self.api_key = "Ff3bAAZyGtK09tos5ZfXZLEvRy_60nkFsVMhy79vvykW6831"
		self.room_ids = ['2','3','4','6']
		#start_timestamp = ms
		#end_timestamp = ms
		self.limit = "100"

	def run(self):
		while running:
			r = requests.post(self.api_url, data = { 'api_key': self.api_key, 'room_id': self.room_ids, 'limit': self.limit })
			self.limit = 5
			#print(dir(r))
			#print(r.json())
			if r.ok == True:
			    c = 0
			    for j in r.json():
			        exists = IFC_Message.query.filter(IFC_Message.message_id == j['message_id'])
			        if exists.count() != 0:
#			            print(str(c) + ': Message allready entered')
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
			        print(m)
			
			time.sleep(10)

def tstream_cleanup():
	print('Performing cleanup...')

if __name__ == '__main__':
	running = True
	print('Running.. ')

	tsc = TwitterSphereConfig()
	ts = TwitterSphere()
	ifr = IFlyReader()

	tsc_t = threading.Thread(target=tsc.run, args=())
	ts_t = threading.Thread(target=ts.run, args=())
	ifr_t = threading.Thread(target=ifr.run, args=())

	tsc_t.start()
	ts_t.start()
	ifr_t.start()

	atexit.register(tstream_cleanup)
	

