from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# import pit_app.views
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

from pit_app.views.home      import home
from pit_app.views.search    import search
from pit_app.views.results   import results
# from pit_app.views.users     import users
# from pit_app.views.data      import data
# from pit_app.views.plots     import plots
# from pit_app.views.auth      import auth

# # Register blueprint(s)
application.register_blueprint(home)
application.register_blueprint(search)
application.register_blueprint(results)
# application.register_blueprint(users)
# application.register_blueprint(data)
# application.register_blueprint(plots)
# application.register_blueprint(auth)

