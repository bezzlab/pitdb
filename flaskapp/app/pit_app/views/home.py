from flask import Blueprint, render_template

home = Blueprint('home',  __name__)

@home.route('/')
def index():
    # Do some stuff
    return render_template('home/index.html')

@home.route('/about')
def about():
  return render_template('home/about.html')

@home.route('/index_tomato')
def tomato():
  return render_template('index_tomato.html')

@home.route('/sunburst')
def sunburst():
  return render_template('sunburst.html')