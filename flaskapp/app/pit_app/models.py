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
  
  name    = db.Column(db.String(255), nullable=False, unique=True) 
  user_id = db.Column('user_id', db.Integer, db.ForeignKey("user.id"))
  
  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return '<Experiment name %r>' % (self.name)


class Sample(Base):
  __tablename__ = 'sample'
  
  name   = db.Column(db.String(255), unique=True)
  exp_id = db.Column('exp_id', db.Integer, db.ForeignKey("experiment.id"))
  
  def __init__(self, name, exp_id):
    self.name   = name
    self.exp_id = exp_id


class TGE(Base):
  __tablename__ = 'tge'
  
  amino_seq = db.Column(db.Text, nullable=False) # unique=True
  type = db.Column(db.String(255))

  def __init__(self, amino_seq, type):
    self.amino_seq = amino_seq
    self.type = type

  def __repr__(self):
    return '<TGE %r>' % (self.amino_seq)


class TGEobservation(Base):
  __tablename__ = 'tge_obs'
  
  tge_id      = db.Column('tge_id',    db.Integer, db.ForeignKey("tge.id"))
  sample_id   = db.Column('sample_id', db.Integer, db.ForeignKey("sample.id"))
  name        = db.Column(db.String(255)) # unique=True
  description = db.Column(db.String(255))
  organism    = db.Column(db.String(255))
  peptide_num = db.Column(db.Integer)
  #uniprot_id  = db.Column(db.String(255))
  #membership  = db.Column(db.String(255))
  
  def __init__(self, name, description, organism, peptide_num):
    self.name        = name
    self.description = description
    self.peptide_num = peptide_num
    self.organism    = organism
    #self.uniprot_id  = uniprot_id
    #self.membership  = membership

  def __repr__(self):
    return '<TGE %r>' % (self.name)


class Transcript(Base):
  __tablename__ = 'transcript'
  
  obs_id    = db.Column('obs_id', db.Integer, db.ForeignKey("tge_obs.id"))
  dna_seq   = db.Column(db.Text, nullable=False)
  ensemble  = db.Column(db.String(255)) 
  assembly  = db.Column(db.String(255))
  chr       = db.Column(db.String(255)) 
  start     = db.Column(db.Integer)
  end       = db.Column(db.Integer)
  
  def __init__(self, dna_seq, ensemble, assembly, chr, start, end):
    self.dna_seq  = dna_seq
    self.ensemble = ensemble
    sef.assembly  = assembly
    self.chr      = chr
    self.start    = start
    self.end      = end
    


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
  
  obs_id     = db.Column('obs_id',     db.Integer, db.ForeignKey("tge_obs.id"), nullable=False)
  peptide_id = db.Column('peptide_id', db.Integer, db.ForeignKey("peptide.id"), nullable=False)

  def __init__(self, obs_id, peptide_id):
    self.obs_id     = obs_id
    self.peptide_id = peptide_id

  def __repr__(self):
    return '<TgeToPeptide %r>' % (self.obs_id)


class PSM(Base):
  __tablename__ = 'psm'
  
  psm_id        = db.Column('tge_pep_id', db.Integer, db.ForeignKey("tge_peptide.id"))
  name          = db.Column(db.String(255))
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

  def __init__(self, name):
    self.name = name
    
  def __repr__(self):
    return '<Spectrum %r>' % (self.name)


# class PeptideToPSM(Base):
#   __tablename__ = 'peptide_psm'
  
#   peptide_id = db.Column('peptide_id', db.Integer, db.ForeignKey("peptide.id"), nullable=False)
#   psm_id     = db.Column('psm_id',     db.Integer, db.ForeignKey("psm.id"), nullable=False)

#   def __init__(self, peptide_id, psm_id):
#     self.peptide_id = peptide_id
#     self.psm_id     = psm_id

#   def __repr__(self):
#     return '<PeptideToPSM %r>' % (self.peptide_id)


class Organism(Base):
  __tablename__ = 'organism'
  
  name = db.Column(db.String(255), nullable=False) # unique=True
  
  def __init__(self, amino_seq):
    self.aa_seq  = aa_seq

  def __repr__(self):
    return '<Organism %r>' % (self.name)

db.create_all()