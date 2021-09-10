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


@app.route('/')
@app.route('/home/')
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


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # Remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route('/recipes', methods=['GET', 'POST'])
def recipes_page():
    recipes = mongo.db.Recipes
    return render_template('recipes.html', all_recipes=recipes.find())


@app.route('/recipes/search', methods=['GET', 'POST'])
def search_data():
    recipes = mongo.db.Recipes
    query_text = request.form.get('search_value')

    if not query_text:
        cursor = recipes.get()

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


@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if request.method == "POST":
        task = {
            "recipe_name": request.form.get("recipe_name"),
            "img_url": request.form.get("img_url"),
            "ingredients": request.form.get("ingredients"),
            "preparation_time": request.form.get("preparation_time"),
            "step_description": request.form.get("step_description"),
            "cooking_time": request.form.get("cooking_time"),
        }
        mongo.db.tasks.insert_one(task)
        flash("Recipe Successfully Added")
        return redirect(url_for("add_recipe"))

    categories = mongo.db.categories.find().sort("recipe_name", 1)
    return render_template("add_recipe.html", categories=categories)


@app.route('/edit_recipe/<recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    if request.method == "POST":
        submit = {
            "recipe_name": request.form.get("recipe_name"),
            "img_url": request.form.get("img_url"),
            "ingredients": request.form.get("ingredients"),
            "preparation_time": request.form.get("preparation_time"),
            "step_description": request.form.get("step_description"),
            "cooking_time": request.form.get("cooking_time"),
            "created_by": session["user"]
        }
        mongo.db.recipe.update({"_id": ObjectId(recipe_id)}, submit)
        flash("Recipe Successfully Updated")

    recipe = mongo.db.tasks.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "edit_recipe.html", recipe=recipe, categories=categories)


@app.route('/update_recipe/<recipe_id>', methods=['GET', 'POST'])
def update_recipe(recipe_id):
    user().update_recipes(recipe_id)
    return redirect(url_for('profile_page'))


@app.route("/delete_recipe/<recipe_id>", methods=['GET'])
def delete_task(task_id):
    mongo.db.recipe.remove({"_id": ObjectId(task_id)})
    flash("Recipe Successfully Deleted")
    return redirect(url_for("profile_page"))


@app.route("/get_categories", methods=['GET'])
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


@app.route('/view_recipe/<recipe_id>', methods=["GET"])
def view_recipe(recipe_id):
    recipes = mongo.db.Recipes
    recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
    ingredients = zip(recipe['recipe_name'])

    return render_template('recipes.html', recipes=recipes,
                           ingredients=ingredients)


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
