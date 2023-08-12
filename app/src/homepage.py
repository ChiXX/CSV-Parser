from flask import Blueprint 

homepage: Blueprint = Blueprint('homepage', __name__)

@homepage.route('/', methods=['GET', 'POST'])
def home() -> str:
    return '<h1>home</h1>' 