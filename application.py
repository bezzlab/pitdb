from flask import Flask
from pit_app import application

# EB looks for an 'application' callable by default.

# run the app.
if __name__ == "__main__":
	# Setting debug to True enables debug output. This line should be removed before deploying a production app.
	#application.run(host='0.0.0.0', port=8080, debug=True)
	application.run(host='127.0.0.1', port=5001, debug=True)