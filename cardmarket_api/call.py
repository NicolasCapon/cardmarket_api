import json
import urllib
import logging
import requests
from functools import wraps
from cardmarket_api import config
from requests_oauthlib import OAuth1


def get_content(endpoint, parameters, credentials, method="GET", data_type=None, data=None):
    """Authenticate to cardmarket API, this method is API v2.0 compatible
       https://www.mkmapi.eu/ws/documentation/API:Auth_OAuthHeader
       Possible methods : GET, POST, PUT, DELETE
       Data needs to be XML formatted and is mandatory for POST & PUT methods"""

    url = config.base_url + "/output.json" + endpoint

    oauth = OAuth1(credentials["mkm_app_token"],
                   client_secret=credentials["mkm_app_secret"],
                   resource_owner_key=credentials["mkm_access_token"],
                   resource_owner_secret=credentials["mkm_token_secret"],
                   realm=url)

    # If query parameters are passed through parameters, add them to the url
    if parameters:
        url += "?" + "&".join(
            ["=".join([key, urllib.parse.quote_plus(str(value))]) for key, value in sorted(parameters.items())])

    if method == "GET":
        r = requests.get(url, auth=oauth, allow_redirects=False)
    elif method == "POST" and data:
        r = requests.post(url, auth=oauth, data=data)
    elif method == "PUT" and data:
        r = requests.put(url, auth=oauth, data=data)
    elif method == "DELETE":
        r = requests.delete(url, auth=oauth)
    else:
        logging.info("Error ! Incorrect method or empty data")
        return False

    logging.info("CardMarket API Request [{}] {}".format(r.status_code, url))

    content = []
    if r.status_code == 200:
        content = json.loads(r.content.decode('utf-8')).get(data_type, None)

    elif r.status_code == 206:
        content = json.loads(r.content.decode('utf-8')).get(data_type, None)
        # Search for a next page of data
        if content and len(content) == 1000:
            parameters["start"] += 1000
            content += get_content(endpoint, method=method, data_type=data_type, data=data, **parameters)["data"]

    elif r.status_code == 307:
        # Too much results, pagination needed
        pagination = {"start": 0, "maxResults": 1000}
        new_parameters = {**parameters, **pagination}
        content += get_content(endpoint, method=method, data_type=data_type, data=data, **new_parameters)["data"]

    # 5000 requests per 24 hours max
    request_count = r.headers.get("X-Request-Limit-Count", 0)
    expires = r.headers.get("Expires", 0)

    return {"data": content, "request_count": request_count, "expires": expires}


def api_request(func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        content = get_content(endpoint=result["endpoint"],
                              parameters=result.get("parameters", None),
                              credentials=self.credentials,
                              method=result.get("method", "GET"),
                              data_type=result.get("data_type", None),
                              data=result.get("data", None))

        self.request_count = content["request_count"]
        self.expires = content["expires"]

        return content["data"]
    return wrapped


if __name__ == "__main__":
    # Tests:
    # LEA giant spider = 5340
    # Max giant spider = 296561
    link = "/articles/5340"
    c = get_content(link, data_type="article")

    # print(list(c.keys()))
    # print(c.get("links", []))
    # print(len(c.get("article", [])))
    print(len(c))
