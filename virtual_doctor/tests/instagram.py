#comment posts on instagram
import requests

url = "https://graph.facebook.com"

response = requests.get(url+'/17895695668004550/comments')
print(response)