import logging
import requests
from tqdm import tqdm
from models import *

USER_FRAG = """
    id
    name
    """
POST_FRAG = """
    id
    title
    description
    author {""" + USER_FRAG + """}
    completed
    reserved
    """
MSG_FRAG = """
    id
    author {""" + USER_FRAG + """}
    post {""" + POST_FRAG + """}
    """


def perform_graphql(query, token=None):
    response = requests.post('https://project-butterfly.herokuapp.com/',
                             headers=None if token is None else {'Authorization': f"Bearer {token}"},
                             json={'query': query})
    if response.status_code == 200:
        logging.debug('GraphQL Response Success')
    else:
        logging.warning(query)
        logging.warning(f"GraphQL Response failed. Status Code: {response.status_code}. Reason: {response.reason}")
    logging.debug(response.json())
    return response.json()


class UserConnection:
    def __init__(self, token, user):
        self.token = token
        self.user = user

    def get_messages(self, post_id):
        return list(map(lambda msg: Message(**msg), filter(lambda msg: msg['post']['id'] == post_id, perform_graphql("""
            {
                getMessagesForPost(id: \"""" + post_id + """\") {
                    id
                    author {
                        id
                    }
                    post {
                        id
                    }
                }
            }""", self.token)['data']['getMessagesForPost'])))

    def create_post(self, title, description, portions, lat, lon, city):
        perform_graphql("""
            mutation {
                createPost(data: {
                    title: "%s"
                    description: "%s"
                    portions: %d
                    lat: %f
                    lon: %f
                    city: "%s"
                }) {
                    title
                }
            }""" % (title, description, portions, lat, lon, city), self.token)

    def delete_post(self, post_id):
        perform_graphql("""
            mutation {
                deletePost(id: "%s") {
                    id
                }
            }""" % post_id, self.token)

    def delete_user(self):
        perform_graphql("""
            mutation {
                deleteUser {
                    name
                }
            }""", self.token)

    def get_my_posts(self):
        return list(map(lambda x: Post(**x), perform_graphql("""{
                myPosts {
                    id
                    completed
                    reserved
                }
            }""", self.token)['data']['myPosts']))

    def delete_all_posts(self):
        my_posts = self.get_my_posts()
        if not my_posts:
            return
        for post in tqdm(my_posts):
            self.delete_post(post['id'])


def create_user(name, phone_number, password):
    user = perform_graphql("""
        mutation {
            createUser(data: {
                name: "%s"
                phoneNumber: "%s"
                password: "%s"
            }) {
                user {
                    id
                }
                token
            }
        }""" % (name, phone_number, password))['data']['createUser']
    return UserConnection(
        user['token'],
        User(
            user['user']['id'],
            name,
            phone_number))


def user_login(phone_number, password):
    query = """
                mutation {
                    login(data: {
                        phoneNumber: "%s"
                        password: "%s"
                    }) {
                        token
                        user {
                            id
                            phoneNumber
                            name
                        }
                    }
                }"""
    user = perform_graphql(query % (phone_number, password))['data']['login']
    return UserConnection(
        user['token'],
        User(
            user['user']['id'],
            user['user']['name'],
            phone_number))


def bulk_login(data):
    """
    data is a 2-dimensional array containing data used to login. Every second-level array must have a structure of
    [0] -> phoneNumber
    [1] -> password
    """
    users = []

    for i in tqdm(data, desc="Login Progress"):
        users.append(user_login(i[0], i[1]))

    return users

