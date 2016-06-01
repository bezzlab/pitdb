from flask import Blueprint, render_template

home = Blueprint('home',  __name__)

@home.route('/')
def index():
  # Do some stuff
  return render_template('home/index.html')

@home.route('/sunburst')
def sunburst():
  return render_template('sunburst.html')