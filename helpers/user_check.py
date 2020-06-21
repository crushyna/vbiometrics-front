from flask import session, redirect, url_for
import requests


class NewUserModel:

    def __init__(self):
        self.user_id = session['user_id']
        self.email = session['email']
        self.merchant_id = session['merchant_id']

        self.next_step_action = 'none'
        self.next_step_phrase = 'none'
        self.next_step_filename = 'none'
        self.next_step_text_id = int

        # self.initial_num_of_samples = 0
        # self.num_of_total_required_samples = 9
        # self.num_of_total_required_texts = 3
        # self.set_of_text_ids = {}
        # self.set_number_of_missing_samples = {}
        # self.set_of_texts_full = {}

    def get_text_info_by_user_id(self):
        url = f"https://vbiometrics-docker.azurewebsites.net/samples/info/byUserId/{self.merchant_id}/{self.user_id}"
        response = requests.request("GET", url)
        if response.status_code not in (200, 404):
            return {'message': 'Database or connection error! @ get_list_of_texts',
                    'status': 'error'}

        response_data = response.json()

        self.next_step_action = response_data['message']
        if self.next_step_action == "Success, all samples ready!":
            return {'message': 'All samples ready!',
                    'status': 'success'}

        self.next_step_phrase = response_data['data']['phrase']
        self.next_step_filename = response_data['data']['sampleFile']
        self.next_step_text_id = response_data['data']['textId']

        # for image generation
        session['text_ids_set'].append(self.next_step_text_id)

        return {'message': 'Requires data',
                'status': 'error'}

    def generate_images(self, data_set):
        global response
        for each_text_id in data_set:
            url = f"https://vbiometrics-docker.azurewebsites.net/image_generator/{self.merchant_id}/{self.user_id}/{each_text_id}"
            response = requests.request("POST", url)

        if response.status_code not in (200, 201):
            return response.json(), response.status_code

        return response.json(), response.status_code


class AuthenticatingUser:

    @staticmethod
    def verify_user(filename: str):

        url = f"https://vbiometrics-docker.azurewebsites.net/verify_voice/{session['merchant_id']}" \
              f"/{session['email']}" \
              f"/{session['text_id']}" \
              f"/{filename}"

        verify_voice_response = requests.request("GET", url)

        if verify_voice_response.status_code == 500:
            return {'message': 'Back-end server error @def verify_user!',
                    'status': 'error',
                    'error': verify_voice_response.json()}

        return verify_voice_response.json()

    @staticmethod
    def get_random_text(merchant_id: int, user_email: str):
        url = f"https://vbiometrics-docker.azurewebsites.net/get_text_phrase/{merchant_id}/{user_email}"
        get_text_phrase_response = requests.request("GET", url)

        if get_text_phrase_response.status_code == 404:
            return {'message': 'User does not exists!',
                    'status': 'error',
                    'data': get_text_phrase_response.json()}
        elif get_text_phrase_response.status_code == 500:
            return {'message': 'Back-end server error @def get_random_text!',
                    'status': 'error',
                    'data': get_text_phrase_response.json()}

        else:
            return get_text_phrase_response.json()
