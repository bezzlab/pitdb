import os 

# Turns on debugging features in Flask
DEBUG = True 

# Configuration for the Flask-Bcrypt extension
BCRYPT_LEVEL = 12 

# For use in application emails
# MAIL_FROM_EMAIL = "me@me.com"

driver = 'postgresql+psycopg2://'

SQLALCHEMY_DATABASE_URI = driver + os.environ['RDS_USERNAME'] + ':' + os.environ['RDS_PASSWORD'] \
													+'@' + os.environ['RDS_HOSTNAME']  +  ':' + os.environ['RDS_PORT'] \
													+ '/' + os.environ['RDS_DB_NAME']

print "***"+SQLALCHEMY_DATABASE_URI

SQLALCHEMY_TRACK_MODIFICATIONS = True