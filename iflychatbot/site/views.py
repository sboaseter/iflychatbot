from flask import Blueprint, render_template, abort, request, redirect, url_for
from jinja2 import TemplateNotFound
from iflychatbot.models.shared import db
from iflychatbot.models.dbmodels import *

site = Blueprint('site', __name__, template_folder='templates', static_folder="/home/twitterbot/public_html/iflychatbot/iflychatbot/static")

@site.route('')
def index():
	try:
		all_sites = Site.query.all()
		all_users = User.query.all()
		all_site_users = Site_User.query.all()
		for s in all_sites:
			s.users = [u for u in all_users if u.id in [asu.user_id for asu in all_site_users if asu.site_id == s.id]]
			s.available_users = [u for u in all_users if u.id not in [asu.user_id for asu in all_site_users if asu.site_id == s.id]]

		return render_template('index.html', all_sites=all_sites)
	except TemplateNotFound:
		abort(404)

@site.route('repeats')
def repeats():
	try:
		all_repeats = IFC_Message.query.filter(IFC_Message.type == 'repeat')
		all_sites = Site.query.all()
		for ar in all_repeats:
			ar.site_name = (s.name for s in all_sites if s.ifc_room_id == int(ar.room_id)).next()
		return render_template('repeats.html', all_repeats=all_repeats)
	except TemplateNotFound:
		abort(404)

@site.route('repeat_toggle/<int:id>/')
def repeat_toggle(id):
	try:
		repeat_message = IFC_Message.query.get(id)
		repeat_message.status = '' if repeat_message.status == 'active' else 'active'
		db.flush()
		return redirect(url_for('site.repeats'))
	except TemplateNotFound:
		abort(404)

@site.route('repeats/<int:id>/', methods=['GET', 'POST'])
def repeat_detail(id):
	try:
		# Save button
		if request.method == 'POST':
			# Save/Edit record
			print('post')
			if request.form['id'] != None: #form as an Id
				try:
						print('id not none')
						form_id = int(request.form['id'])
						form_site_id = int(request.form['site_id'])
						form_from_name = request.form['from_name'].encode('utf-8')
						form_picture_url = request.form['picture_url'].encode('utf-8')
						form_message = request.form['message'].encode('utf-8')
						form_status = 'status' in request.form

						site = Site.query.get(form_site_id)
						if form_id == 0: #New record
							print('id 0')
							new_ifc_message  = IFC_Message()
							new_ifc_message.site_id = form_site_id
							new_ifc_message.room_id = str(site.ifc_room_id)
							new_ifc_message.from_name = form_from_name
							new_ifc_message.picture_url = form_picture_url
							new_ifc_message.message = form_message
							new_ifc_message.status = 'active' if form_status else ''
							new_ifc_message.type = 'repeat'
							db.add(new_ifc_message)
						else:
							print('id not 0')
							new_ifc_message  = IFC_Message.query.get(form_id)
							new_ifc_message.site_id = form_site_id
							new_ifc_message.room_id = str(site.ifc_room_id)
							new_ifc_message.from_name = form_from_name
							new_ifc_message.picture_url = form_picture_url
							new_ifc_message.message = form_message
							new_ifc_message.status = 'active' if form_status else ''
							new_ifc_message.type = 'repeat'
						db.flush()
				except Exception,e:
					print('bad req:' + str(e))
					pass

				
			return redirect(url_for('site.repeats'))

		if id == 0:
			s = IFC_Message()
			s.id = id
			all_sites = Site.query.all()
			return render_template('repeat_detail.html', msg=s, all_sites=all_sites)
		
		s = IFC_Message.query.get(id)
		all_sites = Site.query.all()
		return render_template('repeat_detail.html', msg=s, all_sites=all_sites)

	except TemplateNotFound:
		abort(404)

@site.route('repeat_delete/<int:id>/')
def repeat_delete(id):
	try:
		IFC_Message.query.filter(IFC_Message.id == id).delete()
		db.flush()
		return redirect(url_for('site.repeats'))
	except TemplateNotFound:
		abort(404)

@site.route('sites')
def sites():
	try:
		all_sites = Site.query.all()
		return render_template('sites.html', all_sites=all_sites)
	except TemplateNotFound:
		abort(404)

@site.route('sites/<int:id>/', methods=['GET', 'POST'])
def site_detail(id):
	try:
		# Save button
		if request.method == 'POST':
			# Save/Edit record
			if request.form['id'] != None: #form as an Id
				form_id = int(request.form['id'])
				form_name = str(request.form['name'].encode('utf-8')).lower()
				form_ifc_room_id = int(request.form['ifc_room_id'])
				form_ifc_key = request.form['ifc_key'].encode('utf-8')
				print('Site new/edit: [id: {}, name: {}, ifc_room_id: {}, ifc_key: {}]'.format(form_id, form_name, form_ifc_room_id, form_ifc_key))

				if form_id == 0: #New record
					new_site  = Site()
					new_site.name = form_name
					new_site.ifc_room_id = form_ifc_room_id
					new_site.ifc_key = form_ifc_key
					db.add(new_site)
				else:
					existing_site = Site.query.get(form_id)
					existing_site.name = form_name
					existing_site.ifc_room_id= form_ifc_room_id
					existing_site.ifc_key = form_ifc_key
				db.flush()
				
			return redirect(url_for('site.sites'))

		if id == 0:
			s = Site()
			s.id = id
			return render_template('site_detail.html', site=s)
		
		s = Site.query.get(id)
		return render_template('site_detail.html', site=s)

	except TemplateNotFound:
		abort(404)

@site.route('sites/remove/<int:id>/')
def site_remove(id):
	Site.query.filter(Site.id == id).delete()
	db.flush()
	return redirect(url_for('site.sites'))

#############
### Users ###
#############

@site.route('users')
def users():
	try:
		all_users = User.query.all()
		all_sources = Source.query.all()
		#print(all_users)
		return render_template('users.html', all_users=all_users, all_sources=all_sources)
	except TemplateNotFound:
		abort(404)

@site.route('users/<int:id>/', methods=['GET', 'POST'])
def user_detail(id):
	try:
		# Save button
		if request.method == 'POST':
			# Save/Edit record
			if request.form['id'] != None: #form as an Id
				form_id = int(request.form['id'])
				form_name = str(request.form['name'].encode('utf-8')).lower()
				form_source_id = int(request.form['source_id'])
				form_active = 'active' in request.form
				form_image = request.form['image'].encode('utf-8')
				selected_source = Source.query.get(form_source_id)

				if form_id == 0: #New record
					print('New user')
					new_user = User()
					new_user.name = form_name
					new_user.source_id = form_source_id
					new_user.source_name = selected_source.name
					new_user.active = form_active
					new_user.image = form_image
					db.add(new_user)
					db.flush()
				else:
					existing_user = User.query.get(form_id)
					existing_user.name = form_name
					existing_user.source_id = form_source_id
					existing_user.source_name = selected_source.name
					existing_user.active = form_active
					existing_user.image = form_image
					db.flush()
				
			return redirect(url_for('site.users'))

		if id == 0:
			u = User()
			u.id = id
			s = Source.query.all()
			all_sites = Site.query.all()
			return render_template('user_detail.html', ud=u, all_sources=s, all_sites=all_sites)
		
		s = Source.query.all()
		u = User.query.get(id)
		all_sites = Site.query.all()
		try:
			u.source = next(ms for ms in s if ms.id == u.source_id)	
			my_source_id_str  = next(ms.id_str for ms in s if ms.id == u.source_id)

			tweets_from_source = Source_Tweet.query.filter(Source_Tweet.id_str == my_source_id_str).order_by(Source_Tweet.id.desc()).limit(25) 
		except Exception,e:
			print('Error fetching source for user')
			u.source = Source()
			tweets_from_source = []
			pass
		return render_template('user_detail.html', ud=u, all_sources=s, all_sites=all_sites, tweets_from_source=tweets_from_source)

	except TemplateNotFound:
		abort(404)

@site.route('users/remove/<int:id>/')
def user_remove(id):
	User.query.filter(User.id == id).delete()
	db.flush()
	return redirect(url_for('site.users'))


##############
### Sourcs ###
##############

@site.route('sources')
def sources():
	try:
		all_sources = Source.query.all()
		s_count = len(all_sources)
		
		print(all_sources)
		return render_template('sources.html', all_sources=all_sources, s_count=s_count)
	except TemplateNotFound:
		abort(404)

@site.route('sources/<int:id>/', methods=['GET', 'POST'])
def source_detail(id):
	try:

		# Save button
		if request.method == 'POST':
			# Save/Edit record
			if request.form['id'] != None: #form as an Id
				form_id = int(request.form['id'])
				form_name = str(request.form['name'].encode('utf-8')).lower()
			

				if form_id == 0: #New record
					new_source = Source()
					new_source.name = form_name
					db.add(new_source)
					db.flush()
				else:
					existing_source = Source.query.get(form_id)
					existing_source.name = form_name
					existing_source.id_str = None
					db.flush()
				
			return redirect(url_for('site.sources'))

		if id == 0:
			s = Source()
			s.id = id
			return render_template('source_detail.html', sd=s)
		
		s = Source.query.get(id)
		s.tweets = Source_Tweet.query.filter(Source_Tweet.id_str == s.id_str).order_by(Source_Tweet.id.desc()).limit(25)
		return render_template('source_detail.html', sd=s)

	except TemplateNotFound:
		abort(404)

@site.route('sources/remove/<int:id>/')
def source_remove(id):
	Source.query.filter(Source.id == id).delete()
	db.flush()
	return redirect(url_for('site.sources'))

#simply refresh for latest!
@site.route('feed')
def feed():
	try:
		all_sites = Site.query.all()
		all_users = User.query.all()
		return render_template('feed.html', all_sites=all_sites, all_users=all_users)
	except TemplateNotFound:
		abort(404)

#add/remove site-user record, binary swap
@site.route('siteuser/<int:site_id>/<int:user_id>/')
def siteuser(site_id, user_id):
	try:
		su = Site_User.query.filter(Site_User.site_id == site_id, Site_User.user_id == user_id)
		if su.count() == 0: #Add
			new_su = Site_User()
			new_su.site_id = site_id
			new_su.user_id = user_id
			db.add(new_su)
		else: # Remove
			su.delete()
		db.flush()
		return redirect(url_for('site.index'))
	except Exception, e:
		print('siteuser error: ' + str(e))
		abort(404)
