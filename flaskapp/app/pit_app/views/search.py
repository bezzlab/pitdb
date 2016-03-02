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
    res = Organism.query.all()
  elif request.method =='POST':
    searchOption = request.form['searchOptions']
    searchType   = request.form['searchType']

    if searchOption == 'Accession Number':
      #if searchType == 'exact':
        res = TGE.query.filter_by(id=form.searchArea.data).all()
      #else:
      #  res = TGE.query.filter(TGE.id.contains(form.searchArea.data)).all()
    elif searchOption == 'Amino Acid Sequence':
      if searchType == 'exact':
        res = TGE.query.filter(TGE.amino_seq == form.searchArea.data).all()
      else:
        res = TGE.query.filter(TGE.amino_seq.like("%"+form.searchArea.data+"%")).all()
    else:
      print (searchOption)
      res = TGEobservation.query.filter(TGEobservation.organism == searchOption).all()
    
    connection.close() 

    return render_template('search/results.html', tgeRes=res, searchData=form.searchArea.data, searchType=searchType)

  return render_template('search/form.html', form=form, organism = res)

@search.route('/results')
def results():

  #tgeRes = TGE.query.all()
  #tgeRes = TGE.query.filter_by(id=tge_id)
  tgeRes = request.args['tgeRes']

  if tgeRes:
    return render_template('search/results.html', tgeRes=tgeRes)
  return render_template('/search')
