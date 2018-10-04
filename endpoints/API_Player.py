"""
API_Player class does the following:
a) serves as an interface between the test and API_Interface
b) contains several useful wrappers around commonly used combination of actions
c) maintains the test context/state 
"""
from base64 import b64encode
from .API_Interface import API_Interface
from utils.results import Results
import json
import urllib.parse
import logging
from utils.__init__ import get_dict_item
from conf import api_example_conf as conf


class API_Player(Results):
    "The class that maintains the test context/state"
    
    def __init__(self, url, log_file_path=None):
        "Constructor"
        super(API_Player, self).__init__(
            level=logging.DEBUG, log_file_path=log_file_path)
        self.api_obj = API_Interface(url=url)
        

    def set_auth_details(self, username, password):
        "encode auth details"
        user = username
        password = password
        b64login = b64encode(bytes('%s:%s' %(user, password),"utf-8"))
        return b64login


    def set_header_details(self, auth_details):
        "make header details"
        if auth_details != '' and auth_details is not None:
            user = conf.user_name
            password = conf.password
            headers = {'Authorization': "Basic %s"%(auth_details.decode('utf-8'))}
        else:
            headers = {'content-type': 'application/json'}

        return headers


    def get_cars(self, auth_details):
        "get available cars "
        headers = self.set_header_details(auth_details)
        json_response = self.api_obj.get_cars(headers=headers)
        print (json_response)
        result_flag = True if json_response['response'] == 200 else False
        self.write(msg="Fetched cars list:\n %s"%str(json_response['text']))
        self.conditional_write(result_flag,
                               positive="Successfully fetched cars",
                               negative="Could not fetch cars")

        return json_response


    def get_car(self, car_name, brand, auth_details=None):
        "gets a given car details"
        url_params = {'car_name': car_name, 'brand': brand}
        url_params_encoded = urllib.parse.urlencode(url_params)
        headers = self.set_header_details(auth_details)
        json_response = self.api_obj.get_car(url_params=url_params_encoded,
                                             headers=headers)
        response = json_response
        result_flag = True if response == 200 else False
        self.write(msg='Fetched car details of :%s %s' % (car_name, response))

        #return result_flag

    def add_car(self, car_details, auth_details):
        "adds a new car"
        car_details = conf.car_details
        data = car_details
        headers = self.set_header_details(auth_details)
        response = self.api_obj.add_car(data=data,
                headers=headers)
        result_flag = True if response['response'] == 200 else False
        
        
        return result_flag


    def register_car(self, car_name, brand, auth_details=None):
        "register car"
        params = {'car_name': car_name, 'brand': brand}
        params_encoded = urllib.parse.urlencode(params)
        customer_details = conf.customer_details
        data = customer_details
        headers = self.set_header_details(auth_details)
        json_response = self.api_obj.register_car(params=params_encoded,
                                                  json=data,
                                                  headers=headers)
        response = (json_response['response'])
        result_flag = True if json_response['response'] == 200 else False
        
        
        return result_flag
    
    
    def update_car(self, car_details, car_name='figo', auth_details=None):
        "updates a car"
        data = {'name': car_details['name'],
                'brand': car_details['brand'],
                'price_range': car_details['price_range'],
                'car_type': car_details['car_type']}

        headers = self.set_header_details(auth_details)
        response = self.api_obj.update_car(car_name,json=data,headers=headers)
        Json_response = response['response']['json_response']
        result_flag = True if response['response']['response'] == 200 else False


        return result_flag

    
    def remove_car(self, car_name, auth_details=None):
        "deletes a car entry"
        headers = self.set_header_details(auth_details)
        json_response = self.api_obj.remove_car(car_name,
                                                headers=headers)
        result_flag = True if json_response['response'] == 200 else False

        return result_flag
    

    def get_registered_cars(self, auth_details=None):
        "gets registered cars"
        headers = self.set_header_details(auth_details)
        json_response = self.api_obj.get_registered_cars(headers=headers)
        response = json_response['registered_cars']
        result_flag = True if response['successful'] == True else False
        self.write(msg="Fetched registered cars list:\n %s"%str(json_response))
        self.conditional_write(result_flag,
                               positive='Successfully fetched registered cars list',
                               negative='Could not fetch registered cars list')

        return response


    def delete_registered_car(self, auth_details=None):
        "deletes registered car"
        headers = self.set_header_details(auth_details)
        json_response = self.api_obj.delete_registered_car(headers=headers)
        result_flag = True if json_response['response'] == 200 else False
        self.conditional_write(result_flag,
                               positive='Successfully deleted registered cars',
                               negative='Could not delete registered car')
    
    def verify_car_count(self, expected_count, auth_details):
        "Verify car count"
        self.write('\n*****Verifying car count******')
        car_count = self.get_cars(auth_details)
        car_count = len(car_count['json_response']['cars_list']) 
        result_flag = True if car_count == expected_count else False

        return result_flag

    
    def verify_registration_count(self, expected_count, auth_details):
        "Verify registered car count"
        self.write('\n******Verifying registered car count********')
        car_count = self.get_registered_cars(auth_details)
        car_count = len(car_count['registered'])
        result_flag = True if car_count == expected_count else False

        return result_flag

    def get_user_list(self, auth_details):
        "get user list"
        headers = self.set_header_details(auth_details)
        user_list = {}
        response_code = None

        """if userlist result is none then return http error code"""
        try:
            result = self.api_obj.get_user_list(headers=headers)
            self.write("Request & Response:\n%s\n" % str(result))
        except Exception as e:
            raise e

        return {'user_list': result['user_list'], 'response_code': result['response']}    

    def check_validation_error(self, auth_details=None):
        "verify validatin error 403"
        result = self.get_user_list(auth_details)
        user_list = result['user_list']
        response_code = result['response_code']
        result_flag = False
        msg = ''

        "verify result based on user list and response code"
        if response_code == 403:
            msg = "403 FORBIDDEN: Authentication successful but no access for non admin users"

        elif response_code == 200:
            result_flag = True
            msg = "successful authentication and access permission"

        elif response_code == 401:
            msg = "401 UNAUTHORIZED: Authenticate with proper credentials OR Require Basic Authentication"

        elif response_code == 404:
            msg = "404 NOT FOUND: URL not found"

        else:
            msg = "unknown reason"

        return {'result_flag': result_flag, 'msg': msg}
    