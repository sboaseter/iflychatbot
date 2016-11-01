from iflychatbot import app
from iflychatbot.models.dbmodels import *
from bcolors import bcolors

with app.app_context():
	sites = Site.query.all()
	users = User.query.all()
	sources = Source.query.all()

	print app.url_map

print bcolors.OKGREEN + '===== Sites ({}) ====='.format(len(sites)) + bcolors.ENDC
for s in sites:
	print s
print ''

print bcolors.OKGREEN + '===== Users ({}) ====='.format(len(users)) + bcolors.ENDC
for u in users:
	print u
print ''

print bcolors.OKGREEN + '===== Sources ({}) ====='.format(len(sources)) + bcolors.ENDC
for k in sources:
	print k
print ''

print bcolors.OKGREEN + '[Test complete]' + bcolors.ENDC

