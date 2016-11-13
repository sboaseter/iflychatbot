from flask import Blueprint, request, jsonify
from iflychatbot.models.dbmodels import *
import requests
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

@api.route('/newmsg/<int:id>/')
def newmsg(id):
	print('New message notification: {}'.format(str(id)))
	msg = IFC_Message.query.get(id)
	print(msg)
	return 'Success'

#def _postMsg(

@api.route('/test/', methods=['GET', 'POST'])
def test():
	publishUrl = "https://api.iflychat.com/api/1.1/room/{}/publish"
	api_key = "Ff3bAAZyGtK09tos5ZfXZLEvRy_60nkFsVMhy79vvykW6831"
	uid = 42
	picture_url = ""
	profile_url = "javascript:void(0)"
	message = str(id)
	color = "#222222"
	roles = "0"
	if request.method == 'POST':
		print('post message')
		print(request.json)
		name = request.json['username']
		message = request.json['message']
		room_id = request.json['room_id']
	r = requests.post(publishUrl.format(room_id), data = {'api_key':api_key, 'uid':uid, 'name':name, 'picture_url':picture_url,'profile_url':profile_url,'message':message,'color':color,'roles':roles})
	if r.ok == True:
		return 'Success'
	else:
		return 'Failure'

@api.route('/ifc_chat/', methods=['GET', 'POST'])
def ifc_chat():
	if request.method == 'POST':
		limit = 50
		latest_id = int(request.json['latest_id'])
		#causes one chat room to be populated heavily and the others not.... fix
		if latest_id == -1:
			ifc_messages = IFC_Message.query.order_by(IFC_Message.id.desc()).limit(limit)
		else:
			ifc_messages = IFC_Message.query.filter(IFC_Message.id > latest_id).limit(limit)
		ifc_msg_dict = [{'id':ifc.id, 'name':ifc.from_name, 'text':ifc.message, 'room_id':ifc.room_id} for ifc in ifc_messages.all()]
		ifc_msg_dict.reverse()
		return jsonify(ifc_msg_dict)
	return 'POST only'



