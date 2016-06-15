from flask import Blueprint, render_template
from pit_app import db
from pit_app.models import User

users = Blueprint('users',  __name__)

@users.route('/profile')
def profile():
  user = User.query.filter_by(address="test").first_or_404()
    
  if user == None:
  	flash('User %s not found.' % user)
  	return redirect(url_for('home.index'))
  
  return render_template('users/profile.html', user=user)