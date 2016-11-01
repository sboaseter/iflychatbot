from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+mysqldb://twitterbot:stacked!123@localhost/iflychatbot',
			convert_unicode=True)
db = scoped_session(sessionmaker(autocommit=True, autoflush=False, bind=engine))
#db = scoped_session(sessionmaker(autocommit=True, expire_on_commit=True, autoflush=True, bind=engine))
Base = declarative_base()
Base.query = db.query_property()

def init_db():
	from iflychatbot.models.dbmodels import User, Source, Site

def expire():
	db.expire_all()

