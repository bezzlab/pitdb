import re
import json
import numpy as np

from pit_app import db
from pit_app.models import TGE, TGEobservation, Transcript, Sample, TgeToPeptide, Peptide, Experiment
from flask import Blueprint, render_template
from flask.ext.login import login_required, current_user
from sqlalchemy.sql import func


dashboard = Blueprint('dashboard',  __name__)


@dashboard.route('/summary')
def summary(user_url_slug):
  tge    = TGE.query.filter_by(id=user_url_slug).first_or_404()
  tgeObs = TGEobservation.query.filter_by(tge_id=user_url_slug).all()
  avgPeptNum = TGEobservation.query.with_entities(func.avg(TGEobservation.peptide_num).label('average')).first()

  results  = []
  organism = set()

  for obs in tgeObs: 
  	sample = Sample.query.filter_by(id=obs.sample_id).first()
  	exp    = Experiment.query.filter_by(id=sample.exp_id).first()
  	#transc = Transcript.query.filter_by(obs_id=obs.id).first()
  	tgePep = TgeToPeptide.query.filter_by(obs_id=obs.id).all()

  	tgeType    = re.search("(?<=type:).*?(?=\s)", obs.description).group(0)
  	tgeLength  = re.search("(?<=len:).*?(?=\s)",  obs.description).group(0)
  	tgeStrand  = re.search("(?<=\().*?(?=\))",    obs.description).group(0)

  	peptides = set()
  	organism.add(obs.organism)
  	
  	for peptide in tgePep: 
  		pept = Peptide.query.filter_by(id=peptide.peptide_id).first()
  		peptides.add(pept.aa_seq)

  	results.append({'observation': obs.name, 'sample': sample.name, 'experiment': exp.name, 
      'type': tgeType, 'length': tgeLength, 'strand':tgeStrand, 'organism': obs.organism, 
  		'peptide_num': obs.peptide_num, 'peptides': ', '.join(peptides)})

      #'dna_seq':transc.dna_seq, 

  return render_template('dashboard/summary.html', tge = tge, tgeObs = obs, organisms= list(organism), 
  	avgPeptNum = avgPeptNum, results=results) 
