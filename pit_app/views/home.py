import locale

from flask import Blueprint, render_template
from pit_app.models import *
from pit_app import db
from sqlalchemy.sql import func, distinct

home = Blueprint('home',  __name__)

@home.route('/')
def index():
	expNum  = Experiment.query.with_entities(func.count(distinct(Experiment.id))).scalar()
	smlNum  = Sample.query.with_entities(func.count(distinct(Sample.id))).scalar()
	tges    = TGE.query.with_entities(func.count(distinct(TGE.id))).scalar()

	return render_template('home/index.html', expNum = expNum, smlNum = smlNum, species = 4, tges = separators(tges))

@home.route('/sunburst')
def sunburst():
  return render_template('sunburst.html')


def separators( inputText ):
  locale.setlocale(locale.LC_ALL, 'en_US')
  newText = locale.format("%d", inputText, grouping=True)
  return newText