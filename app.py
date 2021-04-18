import os
from flask import Flask, flash, render_template, jsonify, \
    request, session, redirect, url_for
from flask_pymongo import PyMongo
from passlib.hash import pbkdf2_sha256
from functools import wraps
import uuid
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from bson.json_util import dumps
from os import path
if os.path.exists("env.py"):
    import env


# Database
app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.secret_key = os.environ.get('SECRET_KEY')
mongo = PyMongo(app)

users = mongo.db.user_login_system
recipes = mongo.db.recipe


# Classes
class User:

    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user

        return jsonify(user), 200

    def signup(self):

        # Create the User Object
        user = {
            '_id': uuid.uuid4().hex,
            'name': request.form.get('name').lower(),
            'email': request.form.get('email').lower(),
            'password': request.form.get('password')
        }

        # Encrypt the password
        user['password'] = pbkdf2_sha256.hash(user['password'])

        # Check for existing email adress
        if users.find_one({'email': user['email'].lower()}):
            return jsonify({'error': 'Email adress already in use'}), 400

        if users.insert_one(user):
            return self.start_session(user)

        return jsonify({"error": "Signup_failed"}), 400

    def signout(self):
        session.clear()
        return redirect(url_for('home_page'))

    def login(self):
        email = request.form.get('email').lower()
        user = users.find_one({'email': email})

        if user and pbkdf2_sha256.verify(
                request.form.get('password'),
                user['password']):

            return self.start_session(user)

        return jsonify({'error': 'Invalid login credentials'}), 401

    def insert_recipe(self):
        recipe = {
            'user_id': session['user']['_id'],
            'recipe_name': request.form.get('recipe_name').lower(),
            'img_url': request.form.get('img_url'),
            'ingredients': request.form.getlist('ingredients'),
            'preparation_time': request.form.getlist('preparation_time'),
            'step_description': request.form.getlist('step_description'),
            'cooking_time': request.form.getlist('cooking_time')
        }

        recipes.insert_one(recipe)

        return jsonify({'success': 'Recipe has been added'}), 200

    def update_recipe(self, recipe_id):
        recipe = {
            'user_id': session['user']['_id'],
            'recipe_name': request.form.get('recipe_name').lower(),
            'img_url': request.form.get('img_url'),
            'ingredients': request.form.getlist('ingredients'),
            'preparation_time': request.form.getlist('preparation_time'),
            'step_description': request.form.getlist('step_description'),
            'cooking_time': request.form.getlist('cooking_time')
        }

        recipes.update({'_id': ObjectId(recipe_id)}, recipe)

        return jsonify({'success': 'Recipe has been updated'}), 200


# Decorators
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('home_page'))

    return wrap


def prevent_misuse(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('profile_page'))
        else:
            return f(*args, **kwargs)

    return wrap


@app.route("/")
@app.route("/cuisine")
def cuisine():
    cuisine = mongo.db.cuisine.find()
    return render_template("cuisine.html", cuisine=cuisine)


@app.route('/')
@app.route('/home')
@prevent_misuse
def home_page():
    return render_template('index.html')


@app.route('/recipes', methods=['GET', 'POST'])
def recipes_page():
    recipes = mongo.db.recipe
    value_searched = request.form.get("search_value")
    if value_searched:
        cursor = recipes.aggregate([
            {"$search": {"text": {"path": "recipe_name",
                                  "query": value_searched},
                         "highlight": {"path": "recipe_name"}}},
            {"$project": {
                "_id": 1,
                "img_url": 1,
                "recipe_name": 1,
                "ingredients": 1,
                "preparation_time": 1,
                "step_description": 1,
                "cooking_time": 1,
                "score": {"$meta": "searchScore"}}}])

        return render_template('recipes.html', all_recipes=cursor)

    return render_template('recipes.html', all_recipes=recipes.find())


@app.route('/recipes/search', methods=['GET', 'POST'])
def search_data():
    recipes = mongo.db.recipe
    query_text = request.form.get('search_value')

    if not query_text:
        cursor = recipes.find()

        list_cursor = list(cursor)
        json_data = dumps(list_cursor)

        return json_data, 200

    cursor = recipes.aggregate([
        {"$search": {"text": {"path": "recipe_name", "query": "query_text"},
                     "highlight": {"path": "recipe_name"}}},
        {"$project": {
            "_id": 1,
            "img_url": 1,
            "recipe_name": 1,
            "ingredients": 1,
            "preparation_time": 1,
            "step_description": 1,
            "cooking_time": 1,
            "score": {"$meta": "searchScore"}}}])

    list_cursor = list(cursor)

    if not list_cursor:
        cursor = recipes.find()

        list_cursor = list(cursor)
        json_data = dumps(list_cursor)

        return json_data, 400

    json_data = dumps(list_cursor)

    return json_data, 200


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route("/contact_us", methods=['GET', 'POST'])
def contact_page():
    if request.method == 'POST':
        flash(message="Thanks {}, we have recived your message!".format(
            request.form.get("name")))
    return render_template('contact.html', contact_page="Contact")


@app.route('/signup', methods=['GET', 'POST'])
@prevent_misuse
def signup_page():
    if request.method == 'POST':
        # check if the username exists in db
        existing_user = mongo.db.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("username already exists")
            return redirect(url_for("signup"))

        signup = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one('signup')

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
@prevent_misuse
def login_page():
    if request.method == 'POST':
        # Check if user exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

    if existing_user:

        if check_password_hash(
                existing_user['password'], request.form.get('password')):
            session["user"] = request.form.get("username").lower()
            flash("Welcome, {}".format(request.form.get("username")))

        else:
            # Invalid password match
            flash("Incorrect Username or Password")
            return redirect(url_for("login"))

    else:
        # Username doesen't exists
        flash("Incorect Username or Password")
        return redirect(url_for("login"))
    return render_template('login.html')


@app.route('/user/login', methods=['POST'])
@prevent_misuse
def login():
    user = User()
    return user.login()


@app.route('/profile_page')
@login_required
def profile_page():
    return render_template('profile.html',
                           user_recipes=recipes.find({
                               'user_id': session['user']['_id']}))


@app.route('/profile_page/sign_out')
@login_required
def sign_out():
    user = User()
    return user.signout()


@app.route('/add_recipe', methods=['POST'])
@login_required
def add_recipe():
    return render_template('add_recipe.html')


@app.route('/add_recipe/insert_recipe', methods=['GET', 'POST'])
@login_required
def insert_recipe():
    user = User()
    return user.insert_recipe()


@app.route('/edit_recipe/<recipe_id>')
@login_required
def edit_recipe(recipe_id):
    recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
    ingredients = zip(recipe['ingredient_name'],
                      recipe['ingredient_amount'],
                      recipe['unit'])
    return render_template('edit_recipe.html',
                           user_recipe=recipe,
                           user_ingredient=ingredients)


@app.route('/update_recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
def update_recipe(recipe_id):
    User().update_recipe(recipe_id)
    return redirect(url_for('profile_page'))


@app.route('/delete_recipe/<recipe_id>')
@login_required
def delete_recipe(recipe_id):
    recipes.remove({'_id': ObjectId(recipe_id)})
    return redirect(url_for('profile_page'))


@app.route('/view_recipe/<recipe_id>')
def view_recipe(recipe_id):
    recipes = mongo.db.recipe
    recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
    ingredients = zip(recipe['ingredient_name'],
                      recipe['ingredient_amount'],
                      recipe['unit'])

    return render_template('recipe.html', recipe=recipe,
                           ingredients=ingredients)


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
