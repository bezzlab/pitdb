# from flask import Flask 

# application = api = Flask(__name__)
# from api import controller
# from pit_app import app

# if __name__ == "__main__":
# 	application.run(host='0.0.0.0', port=8080, debug=True)

# # from pit_app import app
# # app.run(debug=True)

from flask import Flask
from pit_app import application

# EB looks for an 'application' callable by default.
# application = Flask(__name__)

# add a rule for the index page.
# application.add_url_rule('/', 'index')

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    # application.debug = True
    application.run(host='0.0.0.0', port=8080, debug=True)