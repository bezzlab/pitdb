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
    org = Observation.query.with_entities(Observation.organism).\
          distinct(Observation.organism).all()
    connection.close()

  elif request.method =='POST':
    searchOption = request.form['searchOptions']
    searchType   = request.form['searchType']
    searchData   = form.searchArea.data

    if searchOption == 'Accession Number':
      return redirect(url_for('results.tge', accession = searchData))
    elif searchOption == 'Amino Acid Sequence':
      return redirect(url_for('search.results', searchType=searchType, searchData = searchData))
    elif searchOption == 'Experiment ID':
      return redirect(url_for('results.experiment', experiment = searchData))
    elif searchOption == 'Uniprot ID':
      return redirect(url_for('results.protein', uniprot = searchData))
    else:
      return redirect(url_for('results.organism', organism = searchOption))

    connection.close() 

    #return render_template('search/results.html', tge=tge, searchData=searchData, searchType=searchType)
    
  return render_template('search/form.html', form=form, organisms = org)

@search.route('/results')
def results():  
  tgeList = []
  
  searchData = request.args['searchData']
  searchType = request.args['searchType']

  if searchType == 'exact':
    tges = TGE.query.filter(TGE.amino_seq == searchData).all()
  else:
    tges = TGE.query.filter(TGE.amino_seq.like("%"+searchData+"%")).all()

    # # For each tge observation: find the sample(s), experiment(s) and organism(s)
    for tge in tges: 
      obs = Observation.query.\
                        join(TGE, TGE.id == Observation.tge_id).\
                        filter_by(id=tge.id)

      obsNum     = obs.count()
      organisms  = obs.distinct(Observation.organism)
      uniprotIDs = obs.distinct(Observation.uniprot_id)
      tgeClass   = obs.distinct(Observation.tge_class).all()
      
      expNum = Sample.query.with_entities(Sample.exp_id).\
                      join(Observation, Observation.sample_id == Sample.id).\
                      join(TGE, TGE.id == Observation.tge_id).\
                      filter_by(id=tge.id).\
                      distinct(Sample.exp_id).count()

      tgeList.append({'accession': tge.accession, 'length': len(tge.amino_seq), 
        'obsNum': obsNum, 'organisms': organisms, 'class': tgeClass,  'uniprotIDs': uniprotIDs, 
        'expNum': expNum, 'class': tge.tge_class, 'uniprotID': tge.uniprot_id})


    return render_template('search/results.html', tgeList = tgeList)

  return render_template('/search')
