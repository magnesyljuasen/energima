#!/usr/bin/env python

import os
from time import time
import requests
from jose import jwt
from cognite.client import ClientConfig, CogniteClient
from cognite.client.credentials import Token

print("hei")

# A standalone example of using keycloak to authenticate to cdf and verify that we are logged inn

project = "energima"
server_url = "https://auth.properate.com"

realm = {
    "energima": "prod",
    "energima-dev": "dev",
    "energima-test": "test"
}

_last_token = None

def token_expired(token):
    header = jwt.get_unverified_claims(token)
    exp = header.get("exp")
    if not exp:
        return True
    exp = int(exp)
    # Renew if token has less than 2 min lifetime left
    remaining = exp - time()
    return remaining < 120

def request_token():
    client_name = "asplan_viak"
    client_secret = "xdevIMhUEpqWjGxjzELJ0Xfof8QVfktx"
    parameters = {
        "client_id": client_name,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded"
    }
    url =  "%s/realms/%s/%s" % (server_url, realm[project], "protocol/openid-connect/token")
    resp = requests.post(url, data=parameters, headers=headers)
    result = resp.json()
    return result.get("access_token")

def token():
    global _last_token
    if _last_token is None or token_expired(_last_token):
        _last_token = request_token()
    return _last_token

client_name = os.environ.get("AUTH_CLIENT_NAME", "read_all")
client_secret = os.environ.get("AUTH_CLIENT_SECRET")

print(client_name)
print(client_secret)

# Set this variable to an app specific name:
cdf_client_name = os.environ.get("COGNITE_CLIENT_NAME", client_name)

cfg = ClientConfig(client_name=cdf_client_name, project=project,
                   credentials=Token(token))
cdf = CogniteClient(cfg)

print(cdf.assets.retrieve(external_id="AH_7224_Gammelbakkan_15,AH_7224_Rådhusvegen_14"))
