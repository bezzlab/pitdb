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

  
  # samples = Sample.query.with_entities(Observation.tge_class, func.count(Observation.tge_class).label('obsCount')).\
  #             group_by(Observation.tge_class).\
  #             filter_by(organism=organism).all()

  # obsObj.join(Sample, Observation.sample_id==Sample.id).\
  #           distinct(Sample.id).all()

  obs   = Observation.query.with_entities(Observation.tge_class, func.count(Observation.tge_class).label('obsCount')).\
            filter_by(organism=organism).\
            group_by(Observation.tge_class).\
            order_by(Observation.tge_class).all()

  for ob in obs: 

    sampleList = []
    samples = Sample.query.with_entities(Sample.name, func.count(Sample.name).label('smplCount')).\
                join(Observation, Observation.sample_id==Sample.id).\
                filter_by(organism=organism, tge_class=ob.tge_class).\
                group_by(Sample.name).all()

    for smpl in samples:
      expList = []

      exps = Experiment.query.with_entities(Experiment.title, func.count(Experiment.title).label('expCount')).\
                join(Sample, Experiment.id==Sample.exp_id ).\
                filter_by(name = smpl.name).\
                group_by(Experiment.title).all()

      for exp in exps:
        pepList =[]

        peptides = TgeToPeptide.query.with_entities(TgeToPeptide.peptide_id, func.count(TgeToPeptide.peptide_id).label('pepCount')).\
                      join(Observation, Observation.id == TgeToPeptide.obs_id).\
                      filter_by(organism=organism, tge_class=ob.tge_class).\
                      group_by(TgeToPeptide.peptide_id).all()

        for pep in peptides:
          pepList.append({ "name": pep.peptide_id, "size": pep.pepCount}) 

        expList.append({ "name": exp.title, "size": exp.expCount, "children": pepList })

      sampleList.append({ "name": smpl.name, "size": smpl.smplCount, "children": expList })  

         

    # for obj in obsObj: 
    #   # pepElem  = TgeToPeptide.query.with_entities(TgeToPeptide.peptide_id, func.count(TgeToPeptide.peptide_id).label('pepCount')).\
    #   #                     group_by(TgeToPeptide.peptide_id).\
    #   #                     filter_by(obs_id=obj.id).all()
    #   smplElem  = Sample.query.with_entities(Sample.name, func.count(Sample.name).label('smplCount')).\
    #                       group_by(Sample.name).\
    #                       filter_by(id=obj.sample_id).all()
    #   print smplElem
    #   break                    
      #pepList.append({ "name": pepElem[0], "size": pepElem[1] })
    # # # print pepElem
    # # pepCount = Observation.query.with_entities(func.sum(Observation.peptide_num)).\
    # #                 filter_by(id=ob[2]).scalar()

    orgList.append({ "name": ob.tge_class, "size": ob.obsCount, "children": sampleList})

  #data = json.dumps(orgList)
  test = {
    "name": "tgeBreakdown",
    "children": orgList
      # "children": [{
      #   "name": "cluster",
      #   "size": ob[1],
      #   "children": [
      #     {"name": "AgglomerativeCluster", "size": 3},
      #     {"name": "CommunityStructure", "size": 3},
      #     {"name": "HierarchicalCluster", "size": 3},
      #     {"name": "MergeEdge", "size": 1}
      #   ]},{
      #   "name": "graph",
      #   "size": 100,
      #   "children": [
      #     {"name": "BetweennessCentrality", "size": 20},
      #     {"name": "LinkDistance", "size": 20},
      #     {"name": "MaxFlowMinCut", "size": 10},
      #     {"name": "ShortestPaths", "size": 10},
      #     {"name": "SpanningTree", "size": 10}
      #   ]},{
      #   "name": "optimization",
      #   "children": [
      #     {"name": "AspectRatioBanker", "size": 30}
      #   ]}
      # ]
  }

  data = json.dumps(test)

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

