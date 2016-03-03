from flask import Blueprint, render_template, request, session, redirect, url_for
# from sqlalchemy.sql import select
# from sqlalchemy import create_engine
from pit_app import db
from psycopg2 import Binary
from datatables import ColumnDT, DataTables
from pit_app.forms import SearchForm
from pit_app.models import *



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
    searchData   = form.searchArea.data

    if searchOption == 'Accession Number':
      return redirect(url_for('results.tge', tge_id = searchData))
    elif searchOption == 'Amino Acid Sequence':
      return redirect(url_for('search.results', searchType=searchType, searchData = searchData))
    elif searchOption == 'Experiment ID':
      return redirect(url_for('results.experiment', experiment = searchData))
    else:
      return redirect(url_for('results.organism', organism = searchOption))

    connection.close() 

    #return render_template('search/results.html', tge=tge, searchData=searchData, searchType=searchType)
    
  return render_template('search/form.html', form=form, organism = org)

@search.route('/results')
def results():  
  tgeRes = []
  # orgs = exps = set()
  tge = None
  searchData = request.args['searchData']
  searchType = request.args['searchType']

  if searchType == 'exact':
    tges = TGE.query.filter(TGE.amino_seq == searchData).all()

  else:
    tges = TGE.query.filter(TGE.amino_seq.like("%"+searchData+"%")).all()

    # # For each tge observation: find the sample(s), experiment(s) and organism(s)
    for tge in tges: 
      organisms = TGEobservation.query.with_entities(TGEobservation.organism).\
        join(TGE, TGE.id == TGEobservation.tge_id).\
        filter_by(id=tge.id).distinct(TGEobservation.organism).all()
      
      obsNum = TGEobservation.query.with_entities(TGEobservation.organism).\
        join(TGE, TGE.id == TGEobservation.tge_id).\
        filter_by(id=tge.id).count()

      expNum = Sample.query.with_entities(Sample.exp_id).\
        join(TGEobservation, TGEobservation.sample_id==Sample.id).\
        join(TGE, TGE.id == TGEobservation.tge_id).\
        filter_by(id=tge.id).\
        distinct(Sample.exp_id).count()

      tgeRes.append({'id': tge.id, 'type': tge.type, 'length': len(tge.amino_seq), 
        'obsNum': obsNum, 'organisms': organisms, 'expNum': expNum})


    return render_template('search/results.html', tgeRes = tgeRes)

  return render_template('/search')
