import json
import random
import string

import config_handler
import graphql_connection
from db_connection import DataAccessObject

database_conn = DataAccessObject()


def login_from_config(config=config_handler.get_default()):
    return graphql_connection.bulk_login(config.get_user_configs().items())


def create_users_from_json(file_name='./data/users.json', config=config_handler.get_default()):
    def generate_password():
        chars = string.ascii_letters + string.digits
        return "".join(random.choices(chars, k=10))

    def generate_phone_number():
        return 'Country Code: 352 National Number: 691' + ''.join(random.choices(string.digits, k=6))

    for name in json.load(open(file_name)):
        password = generate_password()
        phone_number = generate_phone_number()
        print(password, phone_number)
        graphql_connection.create_user(name, phone_number, password, config)


def generate_location() -> ():
    # range: 49.62 - 49.58
    # range: 6.09 - 6.15
    return (49.60 + random.uniform(-0.012, 0.02),
            6.125 + random.uniform(-0.0125, 0.0125))


models = login_from_config()
random_choices = list(range(len(models)))
posts = json.load(open("./data/posts.json", "r"))

for post in posts:
    choice = random.choice(random_choices)
    random_choices.remove(choice)
    location = generate_location()
    models[choice].create_post(post["title"], post['description'], post['portions'], location[0], location[1],
                               "Luxembourg", post['img_url'])

# for model in models:
#     for post in model.get_my_posts():
#         if "Schnecken" != post.title:
#             model.delete_post(post.id)
