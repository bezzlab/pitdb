# This file initializes your application and brings together all of the various components.

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bcrypt import Bcrypt
#from sqlalchemy_searchable import make_searchable

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
# bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
  return render_template('error/404.html'), 404

# Sample HTTP error handling
@app.errorhandler(500)
def errorNew(error):
  return render_template('error/500.html'), 500


from .views.home      import home
from .views.users     import users
from .views.auth      import auth
from .views.search    import search
from .views.results   import results
from .views.data      import data
from .views.plots     import plots

# Register blueprint(s)
app.register_blueprint(home)
app.register_blueprint(users)
app.register_blueprint(auth)
app.register_blueprint(search)
app.register_blueprint(results)
app.register_blueprint(data)
app.register_blueprint(plots)
