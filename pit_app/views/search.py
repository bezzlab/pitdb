from pit_app import db
from pit_app.models import *
from pit_app.forms import SearchForm
from flask import Blueprint, render_template, request, redirect, url_for

search = Blueprint('search',  __name__)

@search.route('/search',  methods=['GET', 'POST'])
def advance():
  form = SearchForm(request.form)

  if request.method == 'GET':
    org = Observation.query.with_entities(Observation.organism).distinct(Observation.organism).all()

  elif request.method =='POST':
    searchOption = request.form['searchOptions']
    searchType   = request.form['searchType']
    searchData   = form.searchArea.data

#     if searchOption == 'Accession Number':
#       return redirect(url_for('results.tge', accession = searchData))
#     elif searchOption == 'Amino Acid Sequence':
#       return redirect(url_for('results.aminoseq', searchType=searchType, searchData = searchData))
#     elif searchOption == 'Experiment ID':
#       return redirect(url_for('results.experiment', experiment = searchData))
#     elif searchOption == 'Uniprot ID':
#       return redirect(url_for('results.protein', uniprot = searchData))
#     else:
#       return redirect(url_for('results.organism', organism = searchOption))

  return render_template('search/form.html', form=form, organisms = org)
