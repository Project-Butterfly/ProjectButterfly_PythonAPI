class Message:
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.author = kwargs['author']['id']


class Post:
    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.title = kwargs["title"]
        self.completed = kwargs["completed"]
        self.reserved = kwargs["reserved"]


class User:
    def __init__(self, user_id, name, phone):
        self.user_id = user_id
        self.name = name
        self.phone = phone
