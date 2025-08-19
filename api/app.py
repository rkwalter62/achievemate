from flask import Flask, render_template
from dotenv import load_dotenv
from main import *

load_dotenv()

app = Flask(__name__)
app.register_blueprint(aiexperts_bp, url_prefix='/Achievemate')

if __name__ == "__main__":
    app.run(debug=True) 
