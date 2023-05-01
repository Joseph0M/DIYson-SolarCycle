import requests
from passlib.context import CryptContext

domain = "http://192.168.0.63:8005/"

#The client should pass the API key in the headers
headers = {
  #'Content-Type': 'application/json',
}
form_data = {
  "username": "app",
  "password": "test"
}
url = domain + "v1/token"
response = requests.post(url, headers=headers,data=form_data)
print(response.text)  

url = domain + "v1/users/get_user"
headers = {
    'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + response.json()['access_token'],
} 
response = requests.get(url, headers=headers)
print(response.text)

#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#print(pwd_context.hash('test'))