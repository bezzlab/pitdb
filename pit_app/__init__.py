# This file initializes your applicationlication and brings together all of the various components.

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import views
#from sqlalchemy_searchable import make_searchable

application = Flask(__name__, instance_relative_config=True)
application.config.from_object('config')
# application.config.from_pyfile('config.py')
# bcrypt = Bcrypt(application)
db = SQLAlchemy(application)

# Sample HTTP error handling
@application.errorhandler(404)
def not_found(error):
  return render_template('error/404.html'), 404

# Sample HTTP error handling
@application.errorhandler(500)
def errorNew(error):
  return render_template('error/500.html'), 500


from views.home      import home
from views.users     import users
from views.auth      import auth
from views.search    import search
from views.results   import results
from views.data      import data
from views.plots     import plots

# Register blueprint(s)
application.register_blueprint(home)
application.register_blueprint(users)
application.register_blueprint(auth)
application.register_blueprint(search)
application.register_blueprint(results)
application.register_blueprint(data)
application.register_blueprint(plots)
