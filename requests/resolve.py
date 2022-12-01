import requests
res = requests.get('http://localhost:5000/nodes/resolve')
print('response from server:',res.text)
dictFromServer = res.json()