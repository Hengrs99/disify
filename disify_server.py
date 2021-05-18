import flask
import os

from flask import request
from dotenv import load_dotenv

app = flask.Flask(__name__)
app.config['DEBUG'] = True


@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    load_dotenv()
    path = os.getenv("PROJECT_PATH") + "tmp.txt"

    with open(path, 'w') as file:
        file.write(code)

    return '<strong>You are now logged in!</strong>'


app.run()
