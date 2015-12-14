from flask import Blueprint, render_template
# Import the database object from the main app module
from pit_app import db

from pit_app.models import User

user = Blueprint('user',  __name__)

@user.route('/profile')
def profile():
    # Do some stuff
    print User.query.filter_by().first()
    # user = User.query.filter_by(id=1).first()
    # if user == None:
    #     flash('User %s not found.' % nickname)
    #     return redirect(url_for('home.index'))

    return render_template('user/profile.html', user=user)