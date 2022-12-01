import requests
dictToSend = {'sender':"senderid", 'recipient':'recipientid', 'amount':123}
res = requests.post('http://localhost:5000/transactions/new', json=dictToSend)
print('response from server:',res.text)
dictFromServer = res.json()