from flask import session
import requests


class NewUserModel:

    def __init__(self):
        self.user_id = session['user_id']
        self.email = session['email']
        self.merchant_id = session['merchant_id']
        self.initial_num_of_samples = 0
        self.num_of_total_required_samples = 9
        self.num_of_total_required_texts = 3
        self.set_of_text_ids = {}
        self.set_number_of_missing_samples = {}
        self.set_of_texts_full = {}

    def get_initial_list_of_texts(self):
        url = f"https://vbiometrics-docker.azurewebsites.net/samples/byUserId/{self.merchant_id}/{self.user_id}"
        response = requests.request("GET", url)
        if response.status_code not in (200, 201):
            return {'message': 'Database or connection error! @ get_list_of_texts',
                    'status': 'error'}

        response_data = response.json()
        text_id_list = []

        for each_element in response_data['data']:
            text_id_list.append(each_element['textId'])

        return set(text_id_list), len(text_id_list)

    def get_missing_texts(self):
        number_of_missing_texts = self.num_of_total_required_texts - len(self.set_of_text_ids)                  # 3 - 0
        url = f"https://vbiometrics-docker.azurewebsites.net/texts/random/{number_of_missing_texts}"            # = 6
        response = requests.request("GET", url)
        if response.status_code not in (200, 201):
            return {'message': 'Database or connection error! @ get_missing_texts',
                    'status': 'error'}

        new_texts_id = []
        new_texts_phrases = []
        response_data = response.json()

        for each_element in response_data['data']['texts']:
            new_texts_id.append(each_element['textId'])
            new_texts_phrases.append(each_element['phrase'])

        self.num_of_total_required_texts = self.num_of_total_required_texts - len(self.set_of_text_ids) - len(set(new_texts_id))        # 3 - 0 - 3     # = 0

        return set(new_texts_id), dict(zip(set(new_texts_id), set(new_texts_phrases)))

    def get_missing_samples(self):
        url = f"https://vbiometrics-docker.azurewebsites.net/samples/byUserId/{self.merchant_id}/{self.user_id}"
        response = requests.request("GET", url)
        if response.status_code not in (200, 201):
            return {'message': 'Database or connection error! @ get_missing_samples',
                    'status': 'error'}

        response_data = response.json()
        result_dict = {}

        for each_text_id in self.set_of_text_ids:
            count_sum = 0
            for each_element in response_data['data']:
                if each_element['textId'] == each_text_id:
                    count_sum += 1
            result_dict.update({each_text_id: 3 - count_sum})

        return result_dict




