import requests
import trafilatura


def get_url(url, params={}):
  response = requests.get(url, params=params)

  if response.status_code == 200:
    data = response.json()
    return data
  else:
    return None

def post_url(url):
  pass

def parse_using_trafilatura(url):
  return trafilatura.extract(trafilatura.fetch_url(url))
