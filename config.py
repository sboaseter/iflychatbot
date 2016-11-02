class Config(object):
	DEBUG = True
	TESTING = False
	SQLALCHEMY_DATABASE_URI = ''
	SQLALCHEMY_TRACK_MODIFICATIONS = True
#	EXPLAIN_TEMPLATE_LOADING =  True

class ProductionConfig(Config):
	print 'ProductionConfig loaded\n'
	SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://twitterbot:stacked!123@localhost/iflychatbot'


class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = ''

class StandaloneConfig(Config):
	print 'StandaloneConfig loaded\n'
	


