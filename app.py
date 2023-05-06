from flask import Flask, render_template, redirect, request, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, LoginManager
import os

from db import get_container_rent_users
from user import User

app = Flask(__name__)
app.secret_key = "fjeiwofj9483fhdusiagoy78qbdaybcf789weqbyc78ebafueil"

login_manager = LoginManager()
login_manager.init_app(app)

def random_id(N = 20):
  import string, random
  return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))

@login_manager.user_loader
def load_user(user_id):
    query = 'SELECT * FROM rent_users u WHERE u.id = @id'
    params = [
        {'name': '@id', 'value': user_id}
    ]
    result = get_container_rent_users().query_items(query, parameters=params)
    items = list(result)
    if not items:
        return None
    item = items[0]
    return User(id=item['id'], email=item['email'])


@login_manager.request_loader
def load_user_from_request(request):
    email = request.form.get('email')
    password = request.form.get('password')
    user_type = request.form.get('user_type')

    if not email or not password or not user_type:
        return None

    query = 'SELECT * FROM rent_users u WHERE u.email = @email AND u.user_type = @type'
    params = [
        {'name': '@email', 'value': email},
        {'name': '@type', 'value': user_type}
    ]

    result = get_container_rent_users().query_items(query, parameters=params, enable_cross_partition_query=True)
    items = list(result)
    if not items:
        return None

    item = items[0]
    if not check_password_hash(item['password'], password):
        return None

    return User(id=item['id'], email=item['email'])


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login/<user_type>', methods=['GET', 'POST'])
def login(user_type):
    if request.method == 'POST':
        user = load_user_from_request(request)
        if not user:
            flash('Invalid username or password')
            return redirect(url_for('login', user_type=user_type))

        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html', user_type=user_type)


@app.route('/signup/<user_type>', methods=['GET', 'POST'])
def signup(user_type):
    query = 'SELECT * FROM rent_users u WHERE u.user_type = @type'
    params = [
        {'name': '@type', 'value': 'landlord'}
    ]
    result = get_container_rent_users().query_items(query, parameters=params, enable_cross_partition_query=True)
    landlords = list(result)

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        if user_type == 'tenant':
            landlord_id = [landlord['id'] for landlord in landlords if request.form['landlord'] == landlord['name']][0]
        else:
            landlord_id = None

        if user_type == 'landlord':
            auth_key = request.form['auth_key']
            if auth_key != os.environ.get("AUTH_KEY"):
                flash("Incorrect Authorization Key")
                return redirect(url_for("signup", user_type=user_type))

        user = load_user_from_request(request)
        if user:
            flash("User already exists!")
            return redirect(url_for('signup', user_type=user_type))

        new_user = {
            'id': random_id(),
            'email': email,
            'password': generate_password_hash(password),
            'first_name': first_name,
            'last_name': last_name,
            'user_type': user_type
        }

        if landlord_id:
            new_user['landlord'] = landlord_id
        
        get_container_rent_users().upsert_item(new_user)
        return redirect(url_for('login', user_type=user_type))


    return render_template('signup.html', user_type=user_type, landlords=landlords)


@app.route('/dashboard')
@login_required
def dashboard():
    return 'woah i am logged in'


if __name__ == '__main__':
    app.run()
