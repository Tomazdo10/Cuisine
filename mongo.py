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
        print("Mongo is connected")
        return conn
    except pymongo.errors.ConnectionFailure as e:
        print("Could not connect to MongoDB: %s") % e


conn = mongo_connect("MONGO_URI")

coll = conn[DATABASE][COLLECTION]

new_docs = [{"user_id": "Cuisine", "recipe_name": "Tandoori Chicken",
             "img_url": "url(https://images.immediate.co.uk/production/volatile/sites/30/2020/08/recipe-image-legacy-id-871507_11-edaf531.jpg)",
             "ingredients": "juice 2 lemons 4 tsp paprika 2 red onions, finely chopped 16 skinless chicken thighs vegetable oil, for brushing For the marinade 300ml Greek yogurt large piece ginger, grated 4 garlic cloves, crushed ¾ tsp garam masala ¾ tsp ground cumin ½ tsp chilli powder ¼ tsp turmeric",
             "preperation_time": "30min",
             "step_description": "STEP 1 Mix the lemon juice with the paprika and red onions in a large shallow dish, Slash each chicken thigh three times, then turn them in the juice and set aside for 10 mins, STEP 2 Mix all of the marinade ingredients together and pour over the chicken, Give everything a good mix, then cover and chill for at least 1 hr, This can be done up to a day in advance, STEP 3 Heat the grill, Lift the chicken pieces onto a rack over a baking tray, Brush over a little oil and grill for 8 mins on each side or until lightly charred and completely cooked through",
             "cooking_time": "20min",
             },
            {
            "name": "recipe_name", "ingredients": "recipe_ingredients",
            "preperation": "preperation_time", "method": "method",
            "time": "cooking_time", "img_url": "image",
            },
            {
            "name": "recipe_name", "ingredients": "recipe_ingredients",
            "preperation": "preperation_time", "method": "method",
            "time": "cooking_time", "img_url": "image"
            },
            {
            "name": "recipe_name", "ingredients": "recipe_ingredients",
            "preperation": "preperation_time", "method": "method",
            "time": "cooking_time", "img_url": "image",
            },
            {
            "name": "recipe_name", "ingredients": "recipe_ingredients",
            "preperation": "preperation_time", "method": "method",
            "time": "cooking_time", "img_url": "image",
            },

            ]

coll.insert_many(new_docs)

documents = coll.find()

for doc in documents:
    print(doc)
