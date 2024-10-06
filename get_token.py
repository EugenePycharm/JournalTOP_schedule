import requests
import json


# Функция для получения токена авторизации
def get_token():
    url = 'https://msapi.top-academy.ru/api/v2/auth/login'

    data = {
        'application_key': "6a56a5df2667e65aab73ce76d1dd737f7d1faef9c52e8b8c55ac75f565d8e8a6",
        'username': "login",
        'password': "parol",
        'id_city': None
    }

    headers = {'Content-Type': 'application/json', 'Referer': 'https://journal.top-academy.ru/'}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_data = response.json()
        return response_data['refresh_token']
    else:
        return 'Error getting token:', response.status_code

