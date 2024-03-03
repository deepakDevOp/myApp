import requests

# #Signup API
# signup_url = 'http://127.0.0.1:8000/userPolls/signup/'
# signup_data = {"username": "shubham", "password": "shubham@123", "email": "shubham@gmail.com"}
# signup_response = requests.post(signup_url, data=signup_data)
# print(signup_response.json())
#
# #Login API
# login_url = 'http://127.0.0.1:8000/userPolls/login/'
# login_data = {"username": "shubham", "password": "shubham@123"}
# # access_token = 'khWFzA77tBddcCjKbmE3FBqDAl4735'
# # headers = {'Authorization': f'Bearer {access_token}'}
# # login_response = requests.post(login_url, headers=headers)
# login_response = requests.post(login_url, data=login_data)
# print(login_response.json())

#delete user API
delete_url = 'http://127.0.0.1:8000/userPolls/delete_user/'
delete_data = {'username': 'shubham'}
# Send a DELETE request to the delete_user API
delete_response = requests.delete(delete_url, params=delete_data)
print(delete_response.json())
