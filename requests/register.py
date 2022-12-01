import requests
dictToSend = {'nodes':["http://192.168.0.5:5000"]}
res = requests.post('http://localhost:5000/nodes/register', json=dictToSend)
print('response from server:',res.text)
dictFromServer = res.json()