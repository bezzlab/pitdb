import re
import simplejson as json

from flask import Blueprint
from sqlalchemy.sql import func, distinct
from pit_app.models import *
from pit_app import db


plots = Blueprint('plots',  __name__)

@plots.route('/tge/<accession>/tge.json')
def tgeJSON(accession):
  tgeList = []
  tge     = TGE.query.filter_by(accession=accession).one()
  obs     = Observation.query.with_entities(Observation.organism, func.count(Observation.organism)).\
                              group_by(Observation.organism).\
                              filter_by(tge_id=tge.id).all()
  
  for ob in obs: 
    tgeList.append({'organism': ob[0] , 'count': ob[1] })

  data = json.dumps(tgeList)

  return data

@plots.route('/tge/<accession>/experiment.json')
def tgeJSON2(accession):
  #data = json.dumps([{'organism': 'HomoSapiens' , 'num': 3}, {'organism': 'Monkey' , 'num': 10}])

  expList = []
  tge     = TGE.query.filter_by(accession=accession).one()
  tgeObs  = Observation.query.filter_by(tge_id=tge.id)
  
  for ob in tgeObs: 
    sample = Sample.query.filter_by(id=ob.sample_id).first()
    exp    = Experiment.query.with_entities(Experiment.title, func.count(Experiment.title)).\
                        group_by(Experiment.title).\
                        filter_by(id=sample.exp_id).all()

    expList.append({'experiment': exp[0] , 'count': exp[1] })

  data = json.dumps(expList)

  return data

@plots.route('/organism/<organism>/organism.json')
def orgJSON(organism):
  orgList = []

  obs = Observation.query.with_entities(Observation.tge_class, func.count(Observation.tge_class)).\
                          group_by(Observation.tge_class).\
                          filter_by(organism=organism).all()
  
  for ob in obs: 
    orgList.append({'tgeClass': ob[0], 'count': ob[1]})

  data = json.dumps(orgList)

  return data


@plots.route('/experiment/<experiment>/experiment.json')
def expJSON(experiment):
  sampleList = []

  samples   = Sample.query.filter_by(exp_id=experiment).all()

  for sample in samples:
    tgePerSample = Observation.query.filter(Observation.sample_id==sample.id).\
                                distinct(Observation.tge_id).count()
    sampleList.append({'id':sample.id, 'name': sample.name, 'tgeNum':tgePerSample })

  data = json.dumps(sampleList)

  return data

