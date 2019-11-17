import img_utils
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


def _perform_graphql(query, token=None):
    response = requests.post('https://project-butterfly.herokuapp.com/',
                             headers=None if token is None else {'Authorization': f"Bearer {token}"},
                             json={'query': query})
    res_json = response.json()
    if response.status_code == 200:
        logging.debug('GraphQL Response Success')
        if "errors" in res_json:
            for error in res_json['errors']:
                logging.warning(f"GraphQL Response Error. Message: {error['message']}")
    else:
        logging.warning(query)
        logging.warning(f"GraphQL Response failed. Status Code: {response.status_code}. Reason: {response.reason}")
    logging.debug(res_json)
    return res_json


class UserConnection:
    def __init__(self, token, user):
        self.token = token
        self.user = user

    def get_messages(self, post_id):
        return list(map(lambda msg: Message(**msg), filter(lambda msg: msg['post']['id'] == post_id, _perform_graphql("""
            {
                getMessagesForPost(id: "%s") {
                    id
                    author {
                        id
                    }
                    post {
                        id
                    }
                }
            }""" % post_id, self.token)['data']['getMessagesForPost'])))

    def create_post(self, title, description, portions, lat, lon, city, img_url=None):
        base_64 = None
        if img_url is not None:
            print("Loading Image from URL")
            base_64 = img_utils.get_as_base64(img_url)

        _perform_graphql("""
            mutation {
                createPost(data: {
                    title: "%s"
                    description: "%s"
                    %s
                    portions: %d
                    lat: %f
                    lon: %f
                    city: "%s"
                }) {
                    title
                }
            }""" % (title, description,
                    ("image: " + f"\"{base_64.decode()}\"") if base_64 is not None else "",
                    portions, lat, lon, city), self.token)

    def create_message(self, text, post_id):
        _perform_graphql("""
            mutation {
                createMessage(data: {
                    text: "%s"
                    post: "%s"
                }) {
                    id
                }
            }""" % (text, post_id), self.token)

    def delete_post(self, post_id):
        _perform_graphql("""
            mutation {
                deletePost(id: "%s") {
                    id
                }
            }""" % post_id, self.token)

    def delete_user(self):
        _perform_graphql("""
            mutation {
                deleteUser {
                    name
                }
            }""", self.token)

    def get_my_posts(self):
        return list(map(lambda x: Post(**x), _perform_graphql("""{
                myPosts {
                    id
                    completed
                    title
                    reserved
                }
            }""", self.token)['data']['myPosts']))

    def delete_all_posts(self):
        my_posts = self.get_my_posts()
        if not my_posts:
            return
        for post in tqdm(my_posts):
            self.delete_post(post['id'])


def create_user(name, phone_number, password, config=None):
    user = _perform_graphql("""
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
    if config is not None:
        config.insert_user_config(phone_number, password)
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
    user = _perform_graphql(query % (phone_number, password))['data']['login']
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
