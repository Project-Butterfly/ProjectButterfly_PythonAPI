from db_connection import DatabaseConnection
from graphql_connection import bulk_login

database_conn = DatabaseConnection()

models = bulk_login(list(
    map(lambda x: ["Country Code: 352 National Number: " + x, "15511551"], ["621621621", "691691691", "661661661"])))

for model in models:
    for post in model.get_my_posts():
        if not post.completed and post.reserved:
            print(post.get_messages(model))