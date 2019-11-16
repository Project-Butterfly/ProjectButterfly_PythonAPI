import base64
import requests


def get_as_base64(img_url):
    return base64.b64encode(requests.get(img_url).content)
