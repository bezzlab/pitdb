from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash
from pit_app import db
from pit_app.forms import LoginForm, SignupForm
from pit_app.models import User


auth = Blueprint('auth',  __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
  form = SignupForm(request.form)
  
  if request.method == 'POST' and form.validate():
    user = User(form.email.data, form.password.data, form.fullname.data)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('home.index'))
  return render_template('auth/signup.html', form=form)


@auth.route('/signin', methods=['GET', 'POST'])
def signin():
  # If sign in form is submitted
  form = LoginForm(request.form)

  # Verify the sign in form
  if form.validate_on_submit():

    user = User.query.filter_by(email=form.email.data).first()

    if user: #and check_password_hash(user.password, form.password.data):

      session['user_id'] = user.id
      # flash('Welcome %s' % user.name)
      # return redirect(url_for('home.index'))
    flash('Wrong email or password', 'error-message')
  return render_template("auth/signin.html", form=form)
