# This is where you define the models of your application. 
# This may be split into several modules in the same way as views.py.
# Import the database object (db) from the main application module

from . import db
from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

# Define a base model for other database tables to inherit
class Base(db.Model):
  __abstract__  = True

  id      = db.Column(db.Integer,   primary_key=True, autoincrement=True)
  created = db.Column(db.DateTime,  default=datetime.utcnow())
  updated = db.Column(db.DateTime,  default=datetime.utcnow(), onupdate=datetime.utcnow())

  def __init__(self):
    self.created = datetime.utcnow()
    self.updated = datetime.utcnow()
 

class User(Base):
  __tablename__ = 'user'
  
  email     = db.Column(db.String(255), nullable=False, unique=True)
  password  = db.Column(db.String(255), nullable=False)
  fullname  = db.Column(db.String(255), nullable=False)
  address   = db.Column(db.String(255), nullable=False)
  
  # experiments = relationship("Experiments", backref="user")

  def __init__(self, email, password, fullname, address):
    self.email    = email
    self.set_password(password)
    self.fullname = fullname
    self.address  = address

  def set_password(self, password):
    self.password = generate_password_hash(password)
   
  def check_password(self, password):
    return check_password_hash(self.password, password)

  def __repr__(self):
    return '<User %r>' % (self.fullname)


class Experiment(Base):
  __tablename__ = 'experiment'
  
  title     = db.Column(db.String(255), nullable=False, unique=True) 
  user_id   = db.Column('user_id', db.Integer, db.ForeignKey("user.id"))
  accession = db.Column(db.String(255))
  description = db.Column(db.String(500))
  publication = db.Column(db.String(500))
  
  def __init__(self, title, description, publication):
    self.title = title
    self.description = description
    self.publication = publication

  def __repr__(self):
    return '<Experiment title %r>' % (self.title)

class ExperimentWiseStat(Base):
  __tablename__ = 'exp_wise_stat'
  exp_id = db.Column('exp_id', db.Integer, db.ForeignKey("experiment.id"))
  sample_num = db.Column(db.Integer)
  tge_num = db.Column(db.Integer)
  trn_num = db.Column(db.Integer)
  pep_num = db.Column(db.Integer)
  psms_num = db.Column(db.Integer)
  var_num = db.Column(db.Integer)

  def __init__(self, exp_id, sample_id, tge_num, trn_num, pep_num, psms_num, var_num):
    self.exp_id   = exp_id
    self.sample_id = sample_id
    self.tge_num = tge_num
    self.trn_num = trn_num
    self.pep_num = pep_num
    self.psms_num = psms_num
    self.var_num = var_num


class ExperimentStat(Base):
  __tablename__ = 'exp_stat'
  exp_id = db.Column('exp_id', db.Integer, db.ForeignKey("experiment.id"))
  sample_id = db.Column('sample_id', db.Integer, db.ForeignKey("sample.id"))
  tge_num = db.Column(db.Integer)
  trn_num = db.Column(db.Integer)
  pep_num = db.Column(db.Integer)
  psms_num = db.Column(db.Integer)
  var_num = db.Column(db.Integer)

  def __init__(self, exp_id, sample_id, tge_num, trn_num, pep_num, psms_num, var_num):
    self.exp_id   = exp_id
    self.sample_id = sample_id
    self.tge_num = tge_num
    self.trn_num = trn_num
    self.pep_num = pep_num
    self.psms_num = psms_num
    self.var_num = var_num

class Sample(Base):
  __tablename__ = 'sample'
  
  name   = db.Column(db.String(255), unique=True)
  exp_id = db.Column('exp_id', db.Integer, db.ForeignKey("experiment.id"))
  description   = db.Column(db.String(255))
  accession = db.Column(db.String(10))

  def __init__(self, name, exp_id, desc):
    self.name   = name
    self.exp_id = exp_id
    self.description = desc


class TGE(Base):
  __tablename__ = 'tge'
  
  accession  = db.Column(db.String(255))
  amino_seq  = db.Column(db.Text, nullable=False) # unique=True
  tge_class  = db.Column(db.String(255))
  uniprot_id = db.Column(db.String(255))
  #ref_source = db.Column(db.String(255))
  #ref_version = db.Column(db.String(255))
  gene_names = db.Column(db.String(255))
  organisms  = db.Column(db.String(255))
  star       = db.Column(db.String(5))

  def __init__(self, amino_seq, type):
    self.amino_seq = amino_seq
    self.type = type

  def __repr__(self):
    return '<TGE %r>' % (self.amino_seq)


class Observation(Base):
  __tablename__ = 'observation'
  
  tge_id        = db.Column('tge_id',    db.Integer, db.ForeignKey("tge.id"))
  sample_id     = db.Column('sample_id', db.Integer, db.ForeignKey("sample.id"))
  name          = db.Column(db.String(255)) # unique=True
  description   = db.Column(db.String(255))
  organism      = db.Column(db.String(255))
  peptide_num   = db.Column(db.Integer)
  uniprot_id    = db.Column(db.String(255))
  protein_name  = db.Column(db.String(255))
  protein_descr = db.Column(db.String(255))
  gene_name     = db.Column(db.String(255))
  tge_class     = db.Column(db.String(255))
  variation     = db.Column(db.Integer)
  long_description = db.Column(db.String(255))
  score         = db.Column(db.Float)
  ref_score      = db.Column(db.Float)
  score_annot    = db.Column(db.String(20))
  star          = db.Column(db.String(5))
  star_str       = db.Column(db.String(10))
  
  def __init__(self, name, description, organism, peptide_num, uniprot_id, star):
    self.name        = name
    self.description = description
    self.peptide_num = peptide_num
    self.organism    = organism
    self.uniprot_id  = uniprot_id
    self.star        = star
    #self.membership  = membership

  def __repr__(self):
    return '<TGE %r>' % (self.name)


class Transcript(Base):
  __tablename__ = 'transcript'
  
  dna_seq   = db.Column(db.Text, nullable=False)
  ensemble  = db.Column(db.String(255)) 
  assembly  = db.Column(db.String(255))
  chrom       = db.Column(db.String(255)) 
  start     = db.Column(db.Integer)
  end       = db.Column(db.Integer)
  #accession = db.Column(db.String(10)) 
  
  def __init__(self, dna_seq, ensemble, assembly, chr, start, end):
    self.dna_seq  = dna_seq
    self.ensemble = ensemble
    self.assembly  = assembly
    self.chrom      = chr
    self.start    = start
    self.end      = end

class Variation(Base):
  __tablename__ = 'variation'

  ref_id  = db.Column(db.String(255))
  pos   = db.Column(db.Integer)
  ref_aa = db.Column(db.String(255))
  alt_aa = db.Column(db.String(255))
  chrom = db.Column(db.String(255))
  var_type = db.Column(db.String(255))

  def __init__(self, ref_id, pos, refAA, altAA, chrom, varType):
    self.ref_id = ref_id
    self.pos = pos
    self.ref_aa = refAA
    self.alt_aa = altAA
    self.chrom = chrom
    self.var_type = varType

class VariationToObservation(Base):
  __tablename__ = 'variation_observation'
  
  obs_id      = db.Column('obs_id', db.Integer, db.ForeignKey("observation.id"))
  var_id      = db.Column('var_id', db.Integer, db.ForeignKey("variation.id"))
  # unique=True
  qual        = db.Column(db.Float)
  qpos        = db.Column(db.Integer)
  peptide_num = db.Column(db.Integer)
  unique_peptides = db.Column(db.String(255)) ##comma separated list of peptides.

  def __init__(self, obs_id, var_id, qual, qpos, peptide_num, unqPeptides):
    self.obs_id       = obs_id
    self.var_id         = var_id
    self.qual         = qual
    self.qpos         = qpos
    self.peptide_num  = peptide_num
    self.unique_peptides     = unqPeptides

class Peptide(Base):
  __tablename__ = 'peptide'
  
  aa_seq = db.Column(db.String(255), nullable=False) # unique=True
  
  def __init__(self, amino_seq):
    self.aa_seq  = aa_seq

  def __repr__(self):
    return '<Peptide %r>' % (self.aa_seq)


# TgeToPeptide = db.Table('tge_peptide', Base.metadata,
#     db.Column('tge_id',     db.Integer, db.ForeignKey("tge.id")),
#     db.Column('peptide_id', db.Integer, db.ForeignKey("peptide.id"))
# )

class TgeToPeptide(Base):
  __tablename__ = 'tge_peptide'
  
  obs_id     = db.Column('obs_id',     db.Integer, db.ForeignKey("observation.id"), nullable=False)
  peptide_id = db.Column('peptide_id', db.Integer, db.ForeignKey("peptide.id"), nullable=False)

  def __init__(self, obs_id, peptide_id):
    self.obs_id     = obs_id
    self.peptide_id = peptide_id

  def __repr__(self):
    return '<TgeToPeptide %r>' % (self.obs_id)


class TranscriptToObservation(Base):
  __tablename__ = 'transcript_observation'
  
  obs_id     = db.Column('obs_id',     db.Integer, db.ForeignKey("observation.id"), nullable=False)
  transcript_id = db.Column('transcript_id', db.Integer, db.ForeignKey("transcript.id"), nullable=False)

  def __init__(self, obs_id, transcript_id):
    self.obs_id     = obs_id
    self.transcript_id = transcript_id

  def __repr__(self):
    return '<TranscriptToObservation %r>' % (self.obs_id)

class PSM(Base):
  __tablename__ = 'psm'
  
  pep_id    = db.Column('pep_id', db.Integer, db.ForeignKey("peptide.id"))
  psm_id        = db.Column(db.String(255))
  spectrum_id   = db.Column(db.Integer)
  title         = db.Column(db.String(255))
  location      = db.Column(db.String(255))
  retention     = db.Column(db.Numeric)
  calc_mz       = db.Column(db.Numeric)
  exp_mz        = db.Column(db.Numeric)
  charge        = db.Column(db.Numeric)
  modifications = db.Column(db.String(255))
  raw_score     = db.Column(db.Numeric)
  denovo_score  = db.Column(db.Numeric)
  spec_evalue   = db.Column(db.Numeric)
  evalue        = db.Column(db.Numeric)
  qvalue        = db.Column(db.Numeric)
  pep_qvalue    = db.Column(db.Numeric)
  local_fdr     = db.Column(db.Numeric)
  q_value       = db.Column(db.Numeric)
  fdr_score     = db.Column(db.Numeric)

  def __init__(self, psm_id):
    self.psm_id = psm_id
    
  def __repr__(self):
    return '<Spectrum %r>' % (self.psm_id)


# class TGEPeptideToPSM(Base):
#   __tablename__ = 'tge_peptide_psm'
  
#   tge_peptide_id = db.Column('tge_peptide_id', db.Integer, db.ForeignKey("tge_peptide.id"), nullable=False)
#   psm_id     = db.Column('psm_id', db.Integer, db.ForeignKey("psm.id"), nullable=False)

#   def __init__(self, tge_peptide_id, psm_id):
#     self.tge_peptide_id = tge_peptide_id
#     self.psm_id     = psm_id

#   def __repr__(self):
#     return '<TGEPeptideToPSM %r>' % (self.tge_peptide_id)

db.create_all()