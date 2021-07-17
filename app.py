import os
from flask import (
    Flask, flash, render_template,
    request, session, redirect, url_for)
from flask_pymongo import PyMongo
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

user = mongo.db.user_login_system
recipes = mongo.db.recipes


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('index.html')


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route("/contact_us", methods=['GET', 'POST'])
def contact_page():
    if request.method == 'POST':
        flash(message="Thanks {}, we have recived your message!".format(
            request.form.get("name")))
    return render_template('contact.html', contact_page="Contact")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("signup"))

        signup = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(signup)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.user.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route('/profile_page')
def profile_page():
    return render_template('profile.html',
                           user_recipes=recipes.find({
                               'user_id': session['user']['_id']}))


@app.route('/profile_page/signout')
def sign_out():
    user = User()
    return user.signout()


@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
    recipes = mongo.db.Recipes
    value_searched = request.form.get("search_value")
    if value_searched:
        cursor = recipes.aggregate([
            {"$search": {"text": {"path": "recipes_name",
                                  "query": value_searched},
                         "highlight": {"path": "recipes_name"}}},
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
    recipes = mongo.db.Recipes
    query_text = request.form.get('search_value')

    if not query_text:
        cursor = recipes.find()

        list_cursor = list(cursor)
        json_data = dumps(list_cursor)

        return json_data, 200

    cursor = recipes.aggregate([
        {"$search": {"text": {"path": "recipes_name", "query": "query_text"},
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



@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    return render_template('add_recipe.html')


@app.route('/add_recipe/insert_recipe', methods=['GET', 'POST'])
def insert_recipe():
    user = User()
    return user.insert_recipe()


@app.route('/edit_recipe/<recipe_id>')
def edit_recipe(recipe_id):
    recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
    ingredients = zip(recipe['ingredients'],
                      recipe['preparation_time'],
                      recipe['step_description'],
                      recipe['cooking_time'])
    return render_template('edit_recipe.html',
                           user_recipe=recipes,
                           user_ingredient=ingredients)


@app.route('/update_recipe/<recipe_id>', methods=['GET', 'POST'])
def update_recipe(recipe_id):
    user().update_recipes(recipe_id)
    return redirect(url_for('profile_page'))


@app.route('/delete_recipe/<recipe_id>')
def delete_recipe(recipe_id):
    recipes.remove({'_id': ObjectId(recipe_id)})
    return redirect(url_for('profile_page'))


@app.route('/view_recipe/<recipe_id>')
def view_recipe(recipe_id):
    recipes = mongo.db.Recipes
    recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
    ingredients = zip(recipe['ingredients'],
                      recipe['preparation_time'],
                      recipe['step_description'],
                      recipe['cooking_time'])

    return render_template('recipe.html', recipe=recipes,
                           ingredients=ingredients)


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
