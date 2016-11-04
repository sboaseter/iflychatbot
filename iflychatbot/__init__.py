from flask import Flask, Blueprint
from iflychatbot.models.shared import init_db
from iflychatbot.models.dbmodels import Site, User, Source
init_db()
from iflychatbot.site.views import site
from iflychatbot.api.views import api

from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.ProductionConfig')
#db.init_app(app)

@app.template_filter('time_ago')
def time_ago_filter(d):
	td = datetime.now() - d
	print(type(d))
	print(d)
	print(td)
	print(datetime.now())
	return int(td.total_seconds())

app.jinja_env.filters['time_ago'] = time_ago_filter

app.register_blueprint(site, url_prefix='/')
app.register_blueprint(api, url_prefix='/api')

#if __name__=='__main__':
#	app.run()
