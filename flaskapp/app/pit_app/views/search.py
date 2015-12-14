from flask import Blueprint, render_template, request, session, redirect, url_for
# from sqlalchemy.sql import select
# from sqlalchemy import create_engine
from pit_app import db
from psycopg2 import Binary
from datatables import ColumnDT, DataTables
from pit_app.forms import SearchForm
from pit_app.models import TGE



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
    query = connection.execute('SELECT id FROM tge where amino_seq = %s', form.searchArea.data)
    tgeID = query.fetchone().id
    connection.close()

    return redirect(url_for('search.results', tge_id=tgeID))
  # Do some stuff
  return render_template('search/advanced.html', form=form)

@search.route('/advanced_search2')
def advance2():
  # Do some stuff
  return render_template('search/advanced2.html')

@search.route('/<tge_id>/results')
def results(tge_id):

  tgeRes = TGE.query.all()
  #tgeRes = TGE.query.filter_by(id=tge_id)
  
  if tgeRes:
    return render_template('search/results.html', tgeRes=tgeRes)
  return render_template('/advanced_search')
