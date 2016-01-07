import re
from flask import Blueprint, render_template
from flask.ext.login import login_required, current_user

# Import the database object from the main app module
from pit_app import db
from pit_app.models import TGE, Transcript, Sample, TgeToPeptide, Peptide


dashboard = Blueprint('dashboard',  __name__)

# @dashboard.url_value_preprocessor
# def get_dashboard_owner(endpoint, values):
#     query = User.query.filter_by(url_slug=values.pop('user_url_slug'))
#     g.profile_owner = query.first_or_404()


@dashboard.route('/summary')
def summary(user_url_slug):
  tge = TGE.query.filter_by(id=user_url_slug).first_or_404()
  trn = Transcript.query.filter_by(tge_id=user_url_slug).first_or_404()
  pep = TgeToPeptide.query.filter_by(tge_id=user_url_slug).all()
  
  peptides = set()

  for peptide in pep: 
  	test = Peptide.query.filter_by(id=peptide.peptide_id).first()
  	peptides.add(test.aa_seq)
  print peptides

  tgeName    = re.search("(?<=asmbl_).*?$", tge.name)
  tgeType    = re.search("(?<=type:).*?(?=\s)", tge.description)
  tgeLength  = re.search("(?<=len:).*?(?=\s)",  tge.description)
  tgeStrand  = re.search("(?<=\().*?(?=\))",    tge.description)
  sampleName = Sample.query.filter_by(id=tge.sample_id).first().name
  
  # tgeID  = tgeID[0:tgeID.find('|')]
  #tgeType = tge.description

  return render_template('dashboard/summary.html', tge = tge, tgeName = tgeName.group(0), trn = trn, type = tgeType.group(0), length=tgeLength.group(0), strand=tgeStrand.group(0), sampleName=sampleName, peptides=list(peptides))
