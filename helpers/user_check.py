from flask import session
import requests


class NewUserModel:

    def __init__(self):
        self.user_id = session['user_id']
        self.email = session['email']
        self.merchant_id = session['merchant_id']
        self.set_of_text_ids = {}
        self.set_number_of_missing_samples = {}

    def get_initial_list_of_texts(self):
        url = f"https://dbapi.pl/samples/byUserId/{self.merchant_id}/{self.user_id}"
        response = requests.request("GET", url)
        if response.status_code not in (200, 201):
            return {'message': 'Database or connection error! @ get_list_of_texts',
                    'status': 'error'}

        response_data = response.json()
        text_id_list = []

        for each_element in response_data['data']:
            text_id_list.append(each_element['textId'])

        return set(text_id_list)

    def get_missing_texts(self):
        number_of_missing_texts = 3 - len(self.set_of_text_ids)
        url = f"https://dbapi.pl/texts/random/{number_of_missing_texts}"
        response = requests.request("GET", url)
        if response.status_code not in (200, 201):
            return {'message': 'Database or connection error! @ get_missing_texts',
                    'status': 'error'}

        new_texts_id = []
        response_data = response.json()

        for each_element in response_data['data']['texts']:
            new_texts_id.append(each_element['textId'])

        return set(new_texts_id)






