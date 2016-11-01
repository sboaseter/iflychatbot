from __future__ import print_function
import sys
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

#from iflychatbot import appa
from iflychatbot.models.shared import db
from iflychatbot.models.dbmodels import *

#Needed?
#init_db()

from colorama import init, Fore
init()

#import codecs


#consumer key, consumer secret, access token, access secret.
ckey="QpBbAaG5j5LQwtISpXHSnMaaZ"
csecret="siWbAxNBq9KojlwcoTnmZqo6yrUNsWAvVhZZ9DOY9nP2wRIUiw"
atoken="2728509485-FJjALLzmjoF4uBWMCWRz7gG2suUGSK9qYQiYI2a"
asecret="eJe1olMUVhK5gxz2RNZYNd4RT5H0zrJmINg2ot8w07Jaw"

api_url = 'http://192.169.141.201/iflychatbot/api/'

users = User.query.all()
sources = Source.query.all()
sources_screen_names = [s.name.lower() for s in sources]

class listener(StreamListener):

		def on_data(self, data):
			all_data = json.loads(data)
			try:
				tweet = all_data["text"]
				username = all_data["user"]["screen_name"].lower()
				id_str = all_data["user"]["id_str"]
			except KeyError:
				print('Tweet with no text: {0}'.format(str(all_data).encode('utf-8')))
				return True

			stdb = Source_Tweet()
			stdb.id_str = id_str.encode('utf-8')
			stdb.screen_name = username.encode('utf-8')
			stdb.text = tweet.encode('utf-8')
			stdb.raw = str(all_data).encode('utf-8')

#			url = 'http://192.169.141.201/iflychatbot/api/'
#			payload = {'screen_name': username.encode('utf-8'), 'tweet': tweet.encode('utf-8')}
#			response = requests.post(url, json=payload)

			if username in sources_screen_names:
				api_url = 'http://192.169.141.201/iflychatbot/api/'
				payload = {'screen_name': username.encode('utf-8'), 'tweet': tweet.encode('utf-8')}
				response = requests.post(api_url, json=payload)

				tweet_color = Fore.GREEN
				username = '_screen_name_' + username
				matched_source = [s.id for s in sources if s.name.lower() == username]
				if len(matched_source) > 0:
					stdb.source_id = matched_source[0]

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
		
#			with open('tweets/{}_{}.txt'.format(username, datetime.now().strftime('%H_%M_%S')), 'w') as text_file:
#				text_file.write(data.encode('utf8'))

#			with open('tweets/all.txt', 'a') as text_file:
#				text_file.write(data.encode('utf8'))

			ts = time.strftime('%d-%m-%Y %H:%M:%S', time.strptime(all_data['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))

			print('[{}] [Local: {}] User: {}\n\t{}\n'.format(datetime.now().strftime('%H:%M:%S'),
													ts,
													Fore.CYAN+ username + Fore.RESET, 
													tweet_color + tweet + Fore.RESET))
			return True

		def on_error(self, status):
				print(status)

print(Fore.GREEN + '=== Setting up stream ===' + Fore.RESET, '\n')


def fetch_missing_ids():
	#Twitternames wihout known id's
	swoid = [s.name for s in sources if s.id_str == None]
	if len(swoid) == 0: return
	user_lookups = api.lookup_users(screen_names=swoid)
	print('user_lookups response:\n{}'.format(user_lookups))

	user_ids = dict([(u.screen_name, u.id_str) for u in user_lookups])
	for k,v in user_ids.items():
		sdb_id = [s.id for s in sources if s.name == k.lower()]
		print('Source Id: {}'.format(sdb_id))
		sdb = Source.query.get(sdb_id)
		sdb.id_str = v
		print('Updated: {} with twitter_id: {}{}{}'.format(k, Fore.GREEN, v, Fore.RESET).encode("utf8"))
		
	#Store to DB
	db.flush()

print(Fore.GREEN + '[Users]' + Fore.RESET)
for u in users:
	print('{}{}{}'.format(Fore.CYAN, u, Fore.RESET))
print('')
print(Fore.GREEN + '[Sources]' + Fore.RESET)
for s in sources:
	print('{}{}{}'.format(Fore.CYAN, s, Fore.RESET))
print('')

# Provide Twitter Dev tokens
auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

# Use API to lookup id's for screen_names`
api = API(auth)

fetch_missing_ids()

twitter_user_ids = [s.id_str for s in Source.query.all() if s.id_str != None]

print('{}{} {}{}'.format(Fore.GREEN, 'Ids to monitor: \n', twitter_user_ids, Fore.RESET))

#print(Fore.CYAN + '=== Streaming users ===\n' + Fore.RESET)
#for u in user_lookups:
#	 print('User: {} [{}]'.format(Fore.GREEN + u.screen_name + Fore.RESET, u.id_str))

twitterStream = Stream(auth, listener())

print('{}{}{}'.format(Fore.GREEN, 'Streaming ...', Fore.RESET))
print(type(twitter_user_ids))

twitterStream.filter(follow=twitter_user_ids)


