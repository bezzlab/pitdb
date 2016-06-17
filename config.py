import os 
import yaml

# Turns on debugging features in Flask
DEBUG = True 

# Configuration for the Flask-Bcrypt extension
BCRYPT_LEVEL = 12 

# For use in application emails
# MAIL_FROM_EMAIL = "me@me.com"

driver = 'postgresql+psycopg2://'

if 'RDS_HOSTNAME' in os.environ:
	SQLALCHEMY_DATABASE_URI = driver + os.environ['RDS_USERNAME'] + ':' + os.environ['RDS_PASSWORD'] \
													+'@' + os.environ['RDS_HOSTNAME']  +  ':' + os.environ['RDS_PORT'] \
													+ '/' + os.environ['RDS_DB_NAME']
else:
	print "can't find the environment variables"
	# SQLALCHEMY_DATABASE_URI = driver + db["test"]["username"]+":"+db["test"]["password"] \
	# 												+"@"+db["test"]["host"]+"/"+db["test"]["database"]

	# BASE_DIR = os.path.abspath(os.path.dirname(__file__)) 
	# stream   = open(os.path.join(BASE_DIR, 'db.yml'), "r")
	# db       = yaml.load(stream)
	# stream.close()
	
	# SQLALCHEMY_DATABASE_URI = driver + db["test"]["username"]+":"+db["test"]["password"] \
	# 												+"@"+db["test"]["host"]+"/"+db["test"]["database"]

SQLALCHEMY_TRACK_MODIFICATIONS = True