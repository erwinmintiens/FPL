import json
import requests


class Person:
    def __init__(self, person_id):
        self.id = person_id
        session = requests.session()
        url = "https://fantasy.premierleague.com/api/entry/" + str(self.id)
        r = requests.get(url)
        print(r.content)
        self.all_info = json.loads(r.content)
        url = "https://fantasy.premierleague.com/api/entry/" + str(self.id) + "/history"
        u = session.get(url)
        self.history = json.loads(u.content)
        print(self.history)


if __name__ == '__main__':
    url = "https://users.premierleague.com/accounts/login/"
    username = input("Username: ")
    password = input("Password: ")
    data = {
        'username': username,
        'password': password
    }

    client = requests.session()

    # Retrieve the CSRF token first
    client.get(url)  # sets cookie
    if 'csrftoken' in client.cookies:
        # Django 1.6 and up
        csrftoken = client.cookies['csrftoken']
    else:
        # older versions
        csrftoken = client.cookies['csrf']

    # if 'sessionid' in client.cookies:
    #     # Django 1.6 and up
    #     sessionid = client.cookies['sessionid']
    # else:
    #     # older versions
    #     sessionid = client.cookies['sessionid']

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': url
    }

    login_data = dict(login=username, password=password, csrfmiddlewaretoken=csrftoken, next='/')
    r = client.post(url, data=login_data, headers=headers)
    print(r.status_code)

    bolle_id = 3992968
    erwin_id = 1986671
    louis_id = 412783
    michiel_id = 4440492
    pieter_id = 4410825
    wouter_id = 3126551
    stijn_id = 3725741
    niels_id = 4578815
    arthur_id = 435872

    url = "https://fantasy.premierleague.com/api/entry/" + str(bolle_id) + "/history"
    u = client.get(url)
    history = json.loads(u.content)
    print(client.cookies)

    bolle = Person(bolle_id)
    print(bolle.history)