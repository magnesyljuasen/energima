import os
from time import time
import requests
from jose import jwt
from cognite.client import ClientConfig, CogniteClient
from cognite.client.credentials import Token

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

#client_name = os.environ.get("asplan_viak", "read_all")
#client_secret = os.environ.get("xdevIMhUEpqWjGxjzELJ0Xfof8QVfktx")

client_name="asplan_viak"
client_secret = "xdevIMhUEpqWjGxjzELJ0Xfof8QVfktx"
# Set this variable to an app specific name:
cdf_client_name = os.environ.get("AH_7224_Gammelbakkan_15", client_name)

cfg = ClientConfig(client_name=cdf_client_name, project=project,
                   credentials=Token(token))
cdf = CogniteClient(cfg)
a = cdf.time_series.retrieve(external_id="TS_7224_Gammelbakkan_15+GB15=320.002-RT401").metadata
print(a)

