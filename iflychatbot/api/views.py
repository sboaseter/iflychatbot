from flask import Blueprint, request, jsonify
from iflychatbot.models.dbmodels import *

api = Blueprint('api', __name__)

@api.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		print('\nTweet:[{}] {}'.format(request.json['screen_name'].encode('utf-8'), request.json['tweet'].encode('utf-8')))
		return jsonify(request.json)
	all_sources = Source.query.all()
	print('api index called!')
	
	return '{"result": "42"}'

