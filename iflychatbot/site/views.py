from flask import Blueprint, render_template, abort, request, redirect, url_for
from jinja2 import TemplateNotFound
from iflychatbot.models.shared import db
from iflychatbot.models.dbmodels import *

site = Blueprint('site', __name__, template_folder='templates', static_folder="/home/twitterbot/public_html/iflychatbot/iflychatbot/static")

@site.route('')
def index():
	try:
		all_sites = Site.query.all()
		all_site_users = Site_User.query.all()
		all_users = User.query.all()
	
		for s in all_sites:
			user_ids = [su.user_id for su in all_site_users if su.site_id == s.id]
			s.users = [u for u in all_users if u.id in user_ids]

			s.available_users = [u for u in all_users if u.id not in user_ids]

		return render_template('index.html',
			all_sites=all_sites,
			all_site_users=all_site_users,
			all_users=all_users)

	except TemplateNotFound:
		abort(404)

@site.route('sites')
def sites():
	try:
		all_sites = Site.query.all()
		print(all_sites)
		return render_template('sites.html', all_sites=all_sites)
	except TemplateNotFound:
		abort(404)

@site.route('users')
def users():
	try:
		all_users = User.query.all()
		all_sources = Source.query.all()
		print(all_users)
		return render_template('users.html', all_users=all_users, all_sources=all_sources)
	except TemplateNotFound:
		abort(404)

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
		s.tweets = Source_Tweet.query.filter(Source_Tweet.id_str == s.id_str).order_by(Source_Tweet.id).limit(25)
		return render_template('source_detail.html', sd=s)

	except TemplateNotFound:
		abort(404)

@site.route('sources/remove/<int:id>/')
def source_remove(id):
	Source.query.filter(Source.id == id).delete()
	db.flush()
	return redirect(url_for('site.sources'))
	


####

@site.route('users/<int:id>/', methods=['GET', 'POST'])
def user_detail(id):
	try:

		# Save button
		if request.method == 'POST':
			# Save/Edit record
			if request.form['id'] != None: #form as an Id
				form_id = int(request.form['id'])
				form_name = str(request.form['name'].encode('utf-8')).lower()
			

				if form_id == 0: #New record
#					new_source = Source()
#					new_source.name = form_name
#					db.add(new_source)
#					db.flush()
					pass
				else:
#					existing_source = Source.query.get(form_id)
#					existing_source.name = form_name
#					existing_source.id_str = None
#					db.flush()
					pass
				
			return redirect(url_for('site.users'))

		if id == 0:
#			s = Source()
#			s.id = id
#			return render_template('user_detail.html', sd=s)
			pass
		
#		s = Source.query.get(id)
		u = User.query.get(id)
#		s.tweets = Source_Tweet.query.filter(Source_Tweet.id_str == s.id_str).order_by(Source_Tweet.id).limit(25)
		return render_template('user_detail.html', ud=u)

	except TemplateNotFound:
		abort(404)

@site.route('users/remove/<int:id>/')
def user_remove(id):
	User.query.filter(User.id == id).delete()
	db.flush()
	return redirect(url_for('site.users'))


#simply refresh for latest!
@site.route('feed')
def feed():
	try:
		return render_template('feed.html')
	except TemplateNotFound:
		abort(404)
