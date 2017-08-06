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

@home.route('/browse')
def browse():
  expStats = db.session.query(ExperimentStat.exp_id, func.count(ExperimentStat.sample_id), func.sum(ExperimentStat.tge_num), func.sum(ExperimentStat.trn_num), func.sum(ExperimentStat.pep_num), func.sum(ExperimentStat.psms_num), func.sum(ExperimentStat.var_num)).group_by(ExperimentStat.exp_id).all()
  experimentList= []
  sampleStats = ExperimentStat.query.all()
  sampleList= []
  for exp in expStats:
  	exp_a = Experiment.query.filter(Experiment.id==exp[0]).all()[0]
  	experimentList.append({'accession':exp_a.accession, 'sample': separators(int(exp[1])), 'tge':separators(int(exp[2])), 'trn': separators(int(exp[3])), 'pep': separators(int(exp[4])), 'psm':separators(int(exp[5])), 'var': separators(int(exp[6]))})

  for samp in sampleStats:
  	exp_a = Experiment.query.filter(Experiment.id==samp.exp_id).all()[0]
  	sample_a = Sample.query.filter(Sample.id==samp.sample_id).all()[0]
  	sampleList.append({'accession':sample_a.accession, 'exp_id': exp_a.accession, 'tge':separators(samp.tge_num), 'trn': separators(samp.trn_num), 'pep': separators(samp.pep_num), 'psm':separators(samp.psms_num), 'var': separators(samp.var_num)})

  return render_template('home/browse.html', experiments = experimentList, samples = sampleList)


def separators( inputText ):
  locale.setlocale(locale.LC_ALL, 'en_US')
  newText = locale.format("%d", inputText, grouping=True)
  return newText

def separators( inputText ):
  locale.setlocale(locale.LC_ALL, 'en_US')
  newText = locale.format("%d", inputText, grouping=True)
  return newText