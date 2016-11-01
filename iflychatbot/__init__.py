from flask import Flask, Blueprint
from iflychatbot.models.shared import init_db
from iflychatbot.models.dbmodels import Site, User, Source
init_db()
from iflychatbot.site.views import site
from iflychatbot.api.views import api


app = Flask(__name__)
app.config.from_object('config.ProductionConfig')
#db.init_app(app)

app.register_blueprint(site, url_prefix='/')
app.register_blueprint(api, url_prefix='/api')

#if __name__=='__main__':
#	app.run()
