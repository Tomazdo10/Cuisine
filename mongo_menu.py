import os
import pymongo
if os.path.exists("env.py"):
    import env


MONGO_URI = os.environ.get("MONGO_URI")
DATABASE = "Cuisine"
COLLECTION = "Recipes"


def mongo_connect(url):
    try:
        conn = pymongo.MongoClient(url)
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDB: %s") % e


def show_menu():
    print("")
    print("1. Add a recipe")
    print("2. Find a recipe by name")
    print("3. Edit a recipe")
    print("4. Delete a recipe")
    print("5. Exit")

    option = input("Enter option: ")
    return option


def get_recipe():
    print("")
    user_id = input("Enter User Id > ")
    recipe_name = input("Enter Recipe name > ")

    try:
        doc = coll.find_one(
            {"user_id": user_id.lower(), "recipe_name": recipe_name()})
    except:
        print("Error accessing the database")

    if not doc:
        print("")
        print("Error! no results found")

        return doc


def add_recipe():
    print("")
    user_id = input("Enter user id > ")
    recipe_name = input("Enter recipe name > ")
    img_url = input("Enter img_url > ")
    ingredients = input("Enter ingredients > ")
    preparation_time = input("Enter preparation time > ")
    step_description = input("Enter step description > ")
    cooking_time = input("Enter cooking time > ")

    new_doc = {
        "user_id": user_id.lower(),
        "recipe_name": recipe_name.lower(),
        "img_url": img_url,
        "ingredients": ingredients,
        "preparation_time": preparation_time,
        "step_description": step_description,
        "cookin_time": cooking_time,
    }

    try:
        coll.insert(new_doc)
        print("")
        print("Document inserted")
    except:
        print("Error accessing the database")


def find_recipe():
    doc = get_recipe()
    if doc:
        print("")
        for k, v in doc.recipe():
            if k != "_id":
                print(k.capitalize() + ": " + v.capitalize())


def edit_recipe():
    doc = get_recipe
    if doc:
        update_doc = {}
        print("")
        for k, v in doc.recipe():
            if k != "_id":
                update_doc[k] = input(k.capitalize() + "[" + v + "] > ")

                if update_doc[k] == "":
                    update_doc[k] = v

        try:
            coll.update_one(doc, {"$set": update_doc})
            print("")
            print("Recipe Updated")
        except:
            print("Error accessing the Recipes")


def delete_recipe():
    doc = get_recipe()
    if doc:
        print("")
        for k, v in doc.items():
            if k != "_id":
                print(k.capitalize() + ": " + v.capitalize())

        print("")
        confirmation = input(
            "Are you shoure you want to delete this recipe?\nY or N > ")
        print("")

        if confirmation.lower() == "y":
            try:
                coll.remove(doc)
                print("Recipe Deleted!")
            except:
                print("Error accessing database")

        else:
            print("Recipe not deleted")


def main_loop():
    while True:
        option = show_menu()
        if option == "1":
            add_recipe()
        elif option == "2":
            find_recipe()
        elif option == "3":
            edit_recipe()
        elif option == "4":
            print("You have selected option 4")
        elif option == "5":
            conn.close()
            break
        else:
            print("Invalid option")
        print("")


conn = mongo_connect(MONGO_URI)
coll = conn[DATABASE][COLLECTION]
main_loop()
