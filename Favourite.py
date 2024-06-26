#L Update 26/6 7:45 PM
import os
import sys
import time
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException

# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Set the title of the command prompt window
os.system("title Coded By Ghalwash")

# Define the path to the verification file
verification_file_path = r'C:\Windows\System32\0409\0xaosha.dll'

# Check if the verification file exists
if os.path.isfile(verification_file_path):
    print("auth Done Welcome to Ghalwash script By @MRfa0gh")
    print()
else:
    print("Unauthorized user detected. Exiting script.")
    # Delete the current script file
    script_path = sys.argv[0]
    os.remove(script_path)
    # Create a Readme file with a warning message
    with open('Readme.txt', 'w') as readme_file:
        readme_file.write("Unauthorized use detected. Exiting script.")
    sys.exit()

url = input("Please enter the URL: ")

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument('--profile-directory=Default')
chrome_options.add_argument('--guest')  # Open Chrome in guest mode
chrome_options.add_argument('--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE dns.adguard.com')  # Set custom DNS

# Initialize WebDriver
driver = uc.Chrome(options=chrome_options)
driver.set_window_size(1500, 1300)

driver.get('https://zefoy.com/')
time.sleep(2.5)
driver.execute_script("window.stop();")

element = driver.find_element(By.CSS_SELECTOR, 'body > div.noscriptcheck > div.ua-check > form > div > div')

location = element.location
size = element.size
driver.save_screenshot('screenshot.png')
im = Image.open('screenshot.png')
left = location['x']
top = location['y']
right = left + size['width']
bottom = top + size['height']
im = im.crop((left, top, right, bottom))
im.save('element_screenshot.png')

# Use Tesseract to extract text from the screenshot
extracted_text = pytesseract.image_to_string(im).strip()

print('Solving Captcha')

# Extract the first word after 'Extracted Text:'
words = extracted_text.split()
first_word = words[0] if words else 'No word extracted'

# Input the first word into the specified element
input_element = driver.find_element(By.XPATH, '/html/body/div[5]/div[2]/form/div/div/div/input')
input_element.send_keys(first_word)

# Press Enter (simulate pressing Enter after inputting the text)
input_element.submit()

time.sleep(1.25)
driver.set_window_size(800, 700)

# Check if specific elements are present
try:
    # Find required buttons and elements
    fav_button = driver.find_element(By.XPATH, '/html/body/div[6]/div/div[2]/div/div/div[7]/div/button')    
    # Click on views button and enter URL
    fav_button.click()
    url_input = driver.find_element(By.XPATH, '/html/body/div[12]/div/form/div/input')
    url_input.send_keys(url)
    print('URL entered')
    time.sleep(1)
    
    # Click on the submit button
    search_key = driver.find_element(By.XPATH, '/html/body/div[12]/div/form/div/div/button')
    time.sleep(1.5)
    search_key.click()
    time.sleep(3.5)
    
    # Main loop to handle submit actions
    while True:
        try:
            # Attempt to find and click the submit key
            submit_key = driver.find_element(By.XPATH, '//*[@id="c2VuZF9mb2xsb3dlcnNfdGlrdG9L"]/div[1]/div/form/button')
            submit_key.click()
            time.sleep(5)
            
            # Print the result of the submit action
            result_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="c2VuZF9mb2xsb3dlcnNfdGlrdG9L"]/span[2]'))
            )
            print(result_element.text)
            print('')
            
            # Perform the next action (clicking search key)
            search_key.click()
        
        except NoSuchElementException:
            search_key.click()
            time.sleep(1)
        
        except Exception as e:
            print(f'An error occurred: {e}')
            break  # Exit the loop if any other exception occurs
    
except Exception as e:
    print(f'An error occurred in the main try block: {e}')

finally:
    # Quit script and close Chrome
    print('There Is error Contact Dev For Fix It @Mrfa0gh')
    driver.quit()
