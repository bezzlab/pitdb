from pit_app import db
from pit_app.models import *
from pit_app.forms import SearchForm
from flask import Blueprint, render_template, request, redirect, url_for, jsonify

search = Blueprint('search',  __name__)

@search.route('/search',  methods=['POST'])
def advance():
  form = SearchForm(request.form)

  searchOption = request.form['searchOptions']
  searchType   = request.form['searchType']
  searchData   = form.searchArea.data

  if searchOption == 'Accession Number':
    return redirect(url_for('results.tge', accession = searchData.upper()))
  elif searchOption == 'Amino Acid Sequence':
    return redirect(url_for('results.aminoseq', searchData = searchData.upper(), searchType=searchType))
  elif searchOption == 'Peptide Sequence':
    return redirect(url_for('results.peptide',  searchData = searchData.upper(), searchType=searchType))
  elif searchOption == 'Experiment ID':
    return redirect(url_for('results.experiment', experiment = searchData))
  elif searchOption == 'Uniprot ID':
    return redirect(url_for('results.protein', uniprot = searchData.upper()))
  else:
    return redirect(url_for('results.organism', organism = searchOption))


@search.route('/autocomplete', methods=['GET'])
def autocomplete():
  results = []
  search = request.args.get('autocomplete')
  
  for mv in TGE.query.filter(accession.like('%' + str(search) + '%')).all():
    results.append(mv[0])
  return jsonify(json_list=results) 

