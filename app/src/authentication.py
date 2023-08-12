from flask import Blueprint 

authentication: Blueprint = Blueprint('authentication', __name__)

@authentication.route('/login', methods=['GET', 'POST'])
def login() -> str:
    return '<h1>login</h1>'

@authentication.route('/logout')
def logout() -> str:
    return '<h1>logout</h1>'

@authentication.route('/sign-up', methods=['GET', 'POST'])
def sing_up() -> str:
    return '<h1>sign up</h1>'