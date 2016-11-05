from flask import Blueprint, request, jsonify
from iflychatbot.models.dbmodels import *

api = Blueprint('api', __name__)

@api.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		print('\nTweet:[{}] {}'.format(request.json['screen_name'].encode('utf-8'), request.json['tweet'].encode('utf-8')))
		return jsonify(request.json)
#	all_sources = Source.query.all()
	tweet = Source_Tweet.query.order_by(Source_Tweet.id.desc()).limit(1)
	
	return jsonify(name=tweet[0].screen_name, text=tweet[0].text)
#	return '{"result": "42"}'

