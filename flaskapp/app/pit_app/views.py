from flask import Flask, render_template, request, redirect, url_for, abort, session
from pit_app import app
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

