from flask import Blueprint, render_template
from flask.ext.login import login_required, current_user

# Import the database object from the main app module
from pit_app import db
from pit_app.models import TGE, Transcript


dashboard = Blueprint('dashboard',  __name__)

# @dashboard.url_value_preprocessor
# def get_dashboard_owner(endpoint, values):
#     query = User.query.filter_by(url_slug=values.pop('user_url_slug'))
#     g.profile_owner = query.first_or_404()


@dashboard.route('/summary')
def summary(user_url_slug):
  tge = TGE.query.filter_by(id=user_url_slug).first_or_404()
  trn = Transcript.query.filter_by(tge_id=user_url_slug).first_or_404()
  return render_template('dashboard/summary.html', tge = tge, trn = trn)
