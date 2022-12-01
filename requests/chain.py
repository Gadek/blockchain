import requests
res = requests.get('http://localhost:5000/chain')
print('response from server:',res.text)
dictFromServer = res.json()