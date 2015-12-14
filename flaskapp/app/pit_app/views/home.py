from flask import Blueprint, render_template

home = Blueprint('home',  __name__)

@home.route('/')
def index():
    # Do some stuff
    return render_template('home/index.html')

@home.route('/about')
def about():
  return render_template('home/about.html')