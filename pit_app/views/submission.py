import os
from pit_app import db
from flask import current_app, request
from pit_app.models import *
#from pit_app.forms import SubmissionForm
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
import site
site.addsitedir('/home/btw796/lib/python2.7/site-packages/')
from validate_email import validate_email
import pandas as pd

submission = Blueprint('submission',  __name__)
#photos = UploadSet('photos', IMAGES)

@submission.route('/submission',  methods=['GET','POST'])
def dataSubmission():
  if request.method == 'POST':
    # check if the post request has the file part
    if 'submissionFile' not in request.files:
        #flash('No file part')
        return render_template('submission/invalid.html', message = "NO file"); #redirect(request.url)
    file = request.files['submissionFile']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        #flash('No selected file')
        return render_template('submission/invalid.html', message = "No selected file"); #redirect(request.url)
    if file and allowed_file(file.filename):
        submitter_name = request.form['uploaderName']
        submitter_email = request.form['uploaderEmail']
        print(submitter_name)
        print(submitter_email)
        is_valid = validate_email(submitter_email,verify=True)
        if is_valid:
          submissionTable = pd.read_table(current_app.config['UPLOAD_FOLDER']+"/submittertable.tsv", header=0)
          filename = secure_filename(file.filename)
          if submissionTable[submissionTable['email']==str(submitter_email)].shape[0]==1: ##It should be one because email adress is unique.
            folder_name = str(submitter_email).replace("@",'at')
            print("Email exist")
            if os.path.isdir(os.path.join(current_app.config['UPLOAD_FOLDER'],folder_name)):
              print("Folder exist for the email")
              file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],folder_name, filename))
            else:
              print("This folder should exist")
              os.makedirs(os.path.join(current_app.config['UPLOAD_FOLDER'],folder_name))
              file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],folder_name, filename))
          else:
            print("user email does not exist")
            submissionTable.append({'name':submitter_name,'email':submitter_email}, ignore_index=True)
            folder_name = str(submitter_email).replace("@",'at')
            if os.path.isdir(os.path.join(current_app.config['UPLOAD_FOLDER'],folder_name)):
              print("This folder should not exist")
              file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],folder_name, filename))
            else:
              os.makedirs(os.path.join(current_app.config['UPLOAD_FOLDER'],folder_name))
              file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],folder_name, filename))
        else:
          return render_template('submission/invalid.html', message = "The email address you provided is not a valid email adress.");
    else:
      return render_template('submission/invalid.html', message = "This file type is not allowed to submit")
  return render_template('submission/datasubmission.html');
# def dataSubmission():
#   form = SubmissionForm(CombinedMultiDict((request.files, request.form))) #request.form
#   print("in submission")
#   print(current_app.config['UPLOAD_FOLDER'])
#   print(request.files)
#   #print(form.submissionFile)
#   if form.validate_on_submit():
#     print(form.subFile.data)
#     f=form.subFile.data
#     filename = secure_filename(f.filename)
#     print(filename)
#     print(f)
#     #file_data = request.FILES[form.submissionFile.name].read()
#     #open(os.path.join(UPLOAD_PATH, form.image.data), 'w').write(image_data)
#   else:
#     print('form.subFile.data is false')
#     print(form.subFile.data)
#     print( form.subFile)
  # if form.validate():
  #   f = form.submissionFile.data
  #   filename = secure_filename(f.filename)
  #   print(filename)
  #   print(application.config['UPLOAD_FOLDER'])
  #   if allowed_file(filename):
  #     file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
  # else:
  #   print("form did not validate")
  # if form.file.submissionFile == '':
  #   flash('No selected file')
  #   return redirect(request.url)
  # if form.file and allowed_file(form.file.submissionFile):
  #   filename = secure_filename(form.file.submissionFile)
  #   file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
  #return render_template('submission/datasubmission.html', form=form);
  

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
