from flask import Blueprint, render_template, request, session, redirect, url_for
# from sqlalchemy.sql import select
# from sqlalchemy import create_engine
from pit_app import db
from psycopg2 import Binary
from datatables import ColumnDT, DataTables
from pit_app.forms import SearchForm
from pit_app.models import TGE, Transcript, Organism, TGEobservation



search = Blueprint('search',  __name__)

@search.route('/search',  methods=['GET', 'POST'])
def advance():
  form = SearchForm(request.form)

  connection = db.engine.connect()
  trans = connection.begin()

  if request.method == 'GET':
    org = Organism.query.all()
    connection.close()

  elif request.method =='POST':
    searchOption = request.form['searchOptions']
    searchType   = request.form['searchType']

    if searchOption == 'Accession Number':
      tge = TGE.query.filter_by(id=form.searchArea.data).one_or_none()

    elif searchOption == 'Amino Acid Sequence':
      if searchType == 'exact':
        tge = TGE.query.filter(TGE.amino_seq == form.searchArea.data).all()
      else:
        tge = TGE.query.filter(TGE.amino_seq.like("%"+form.searchArea.data+"%")).all()
    else:
      #tge = TGEobservation.query.filter(TGEobservation.organism == searchOption).all()
      return render_template('results/organism.html', org = searchOption)
    
    connection.close() 

    return render_template('search/results.html', tge=tge, searchData=form.searchArea.data, searchType=searchType)

  return render_template('search/form.html', form=form, organism = org)

@search.route('/results')
def results():  
  results = []
  orgs = exps = set()
  tge  = request.args['tge']

  if tgeRes:
    # Get all the observations of a TGE
    tgeObs = TGEobservation.query.filter_by(tge_id=tge.id).all()
    
    # For each tge observation: find the sample(s), experiment(s) and organism(s)
    for obs in tgeObs: 
      sample = Sample.query.filter_by(id=obs.sample_id).first()
      exp    = Experiment.query.filter_by(id=sample.exp_id).first()

      orgs.add(obs.organism)
      exps.add(exp.name)

    results.append({'tge': tge.id, 'experiments': list(exps), 'organisms': list(orgs) })
       
    return render_template('search/results.html', results = results)

  return render_template('/search')
