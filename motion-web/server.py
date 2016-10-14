import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    values = ''
    for f in os.listdir('.'):
        values += '{}\n'.format(f)
    return "Hello World!\n" + values

if __name__ == "__main__":
    app.run()
