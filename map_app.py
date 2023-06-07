import os
from time import time
import requests
from jose import jwt
from cognite.client import ClientConfig, CogniteClient
from cognite.client.credentials import Token
from _map import Map
from folium import IFrame


#--
import streamlit as st
from streamlit_extras.chart_container import chart_container
import plotly.express as px

#-------
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


#-------

# A standalone example of using keycloak to authenticate to cdf and verify that we are logged inn
project = "energima"
server_url = "https://auth.properate.com"

realm = {
    "energima": "prod",
    "energima-dev": "dev",
    "energima-test": "test"
}

_last_token = None

client_name="asplan_viak"
client_secret = "xdevIMhUEpqWjGxjzELJ0Xfof8QVfktx"
# Set this variable to an app specific name:
cdf_client_name = os.environ.get("AH_7224_Gammelbakkan_15", client_name)

cfg = ClientConfig(client_name=cdf_client_name, project=project,
                credentials=Token(token))
cdf = CogniteClient(cfg)
#--------------------------------------------------------------------------------------------------------------
external_id_list = cdf.time_series.list().to_pandas()["external_id"]
#
selected_time_series = external_id_list[4]
df = cdf.time_series.data.retrieve(external_id=selected_time_series).to_pandas()
metadata = cdf.time_series.retrieve(external_id=selected_time_series).to_pandas().T

fig =px.scatter(x=range(10), y=range(10))
fig.write_html("figur.html")
figure_data = df[selected_time_series][-5:].to_numpy()


# Kart 
map_obj = Map()
map_obj.address_lat = 63.28629
map_obj.address_long = 10.26335
map_obj.address_name = "Gammelbakkan 15"
map_obj.create_wms_map(selected_zoom = 17, figure_data = figure_data)
map_obj.show_map()
