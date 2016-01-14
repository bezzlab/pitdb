from flask import Blueprint, render_template, request, session, redirect, url_for
# from sqlalchemy.sql import select
# from sqlalchemy import create_engine
from pit_app import db
from psycopg2 import Binary
from datatables import ColumnDT, DataTables
from pit_app.forms import SearchForm
from pit_app.models import TGE, Transcript



search = Blueprint('search',  __name__)

@search.route('/search')
def simple():
  # Do some stuff
  return render_template('search/simple.html')

@search.route('/advanced_search',  methods=['GET', 'POST'])
def advance():
  form = SearchForm(request.form)

  if request.method == 'POST':
    connection = db.engine.connect()
    trans = connection.begin()

    searchOption = request.form['searchOptions']
    searchType   = request.form['searchType']

    if searchOption == 'Accession Number':
      if searchType == 'exact':
        res = TGE.query.filter_by(id=form.searchArea.data).all()
      else:
        res = TGE.query.filter(TGE.id.contains(form.searchArea.data)).all()
    elif searchOption == 'Amino Acid Sequence':
      if searchType == 'exact':
        res = TGE.query.filter(TGE.amino_seq == form.searchArea.data).all()
      else:
        res = TGE.query.filter(TGE.amino_seq.like("%"+form.searchArea.data+"%")).all()
    elif searchOption == 'Transcript Sequence':
      if searchType == 'exact':
        res = TGE.query.join(Transcript, TGE.id == Transcript.obs_id).filter(Transcript.dna_seq.like(form.searchArea.data)).all()
        print res
      else:
        res = TGE.query.join(Transcript, TGE.id == Transcript.obs_id).filter(Transcript.dna_seq.like("%"+form.searchArea.data+"%")).all()
        print res
    
    connection.close() 

    return render_template('search/results.html', tgeRes=res, searchData=form.searchArea.data, searchType=searchType)

    #return redirect(url_for('search.results', tgeRes=tgeRes))
  # Do some stuff
  return render_template('search/advanced.html', form=form)

@search.route('/advanced_search2')
def advance2():
  # Do some stuff
  return render_template('search/advanced2.html')

@search.route('/results')
def results():

  #tgeRes = TGE.query.all()
  #tgeRes = TGE.query.filter_by(id=tge_id)
  tgeRes = request.args['tgeRes']
  # print tgeRes

  if tgeRes:
    return render_template('search/results.html', tgeRes=tgeRes)
  return render_template('/advanced_search')
