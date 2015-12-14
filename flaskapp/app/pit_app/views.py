# This is where the routes are defined. It may be split into a package of its own (yourapp/views/) 
# with related views grouped together into modules. /yourapp/models.py	

from pit_app import app

from flask import Flask, render_template, request, redirect, url_for, abort, session

from .forms import EmailPasswordForm
from .models import DBSession, User
from datatables import ColumnDT, DataTables


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error/500.html'), 500

@app.route('/simple_example', methods="GET")
def simple_example():
    # defining columns
    request.GET = request.args.get

    columns = []
    columns.append(ColumnDT('id'))
    columns.append(ColumnDT('full_name'))
    columns.append(ColumnDT('address')) # where address is an SQLAlchemy Relation
    columns.append(ColumnDT('created', filter=str))

    # defining the initial query depending on your purpose
    # query = DBSession.query(User)
    query = User.query

    # instantiating a DataTable for the query and table needed
    rowTable = DataTables(request, User, query, columns)

    # returns what is needed by DataTable
    return rowTable.output_result()

 
# # class User():
# #     __tablename__ = 'user'
    
# #     user_id     = Column(Integer,     primary_key=True)
# #     full_name   = Column(String(255), nullable=False)
# #     address     = Column(String(255), nullable=False)
# #     institution = Column(String(255), nullable=False)


# @app.route('/signup', methods=['POST'])
# def signup():
#     session['username'] = request.form['username']
#     session['message'] = request.form['message']
#     return redirect(url_for('message'))

# @app.route('/message')
# def message():
#     if not 'username' in session:
#         return abort(403)
#     return render_template('message.html', username=session['username'], 
#                                            message=session['message'])


# # # Save e-mail to database and send to success page
# # @app.route('/prereg', methods=['POST'])
# # def prereg():
# #     email = None
# #     if request.method == 'POST':
# #         email = request.form['email']
# #         # Check that email does not already exist (not a great query, but works)
# #         if not db.session.query(User).filter(User.email == email).count():
# #             reg = User(email)
# #             db.session.add(reg)
# #             db.session.commit()
# #             return render_template('success.html')
# #     return render_template('index.html')
