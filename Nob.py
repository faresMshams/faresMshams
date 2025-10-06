#12 update
import asyncio, time, re, yaml
from playwright.async_api import async_playwright
from colorama import init, Fore, Style

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

NUM_BROWSERS = config.get("num_of_browsers", 1)
shown_raw = str(config.get("shown", "Y")).strip().upper()
SHOWN = shown_raw == "Y"
COUNTRY = config["country"].strip().upper()

EMAILS_FILE = "email.txt"
PHONES_FILE = "phone.txt"
PROXIES_FILE = "proxy.txt"
DONE_FILE = "Done.txt"

init(autoreset=True)
BANNER_COLOR = Fore.RED

banner = """
                        ██████╗ ██╗  ██╗ █████╗ ██╗     ██╗    ██╗ █████╗ ███████╗██╗  ██╗
                       ██╔════╝ ██║  ██║██╔══██╗██║     ██║    ██║██╔══██╗██╔════╝██║  ██║
                       ██║  ███╗███████║███████║██║     ██║ █╗ ██║███████║███████╗███████║
                       ██║   ██║██╔══██║██╔══██║██║     ██║███╗██║██╔══██║╚════██║██╔══██║
                       ╚██████╔╝██║  ██║██║  ██║███████╗╚███╔███╔╝██║  ██║███████║██║  ██║
                        ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                           🚀 Apple Script BY @Mrfa0gh 🚀
"""
for line in banner.splitlines():
    print(f"{BANNER_COLOR}{line}{Style.RESET_ALL}")

print(f"Num browsers: {NUM_BROWSERS}, Show browser: {SHOWN} (raw: {shown_raw}), Country: {COUNTRY}")

answers_map = {
    "What is the first name of your best friend in high school?": "eng1",
    "What is your dream job?": "eng2",
    "In what city did your parents meet?": "eng3",
}

file_lock = asyncio.Lock()
ipv4_re = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")

async def pop_line_from_file(path):
    async with file_lock:
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [ln.rstrip("\n") for ln in f.readlines()]
        except FileNotFoundError:
            return None
        if not lines:
            return None
        first = lines.pop(0)
        with open(path, "w", encoding="utf-8") as f:
            if lines:
                f.write("\n".join(lines) + "\n")
        return first.strip()

async def push_line_to_file(path, line):
    async with file_lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line.rstrip("\n") + "\n")

async def append_done_line(mail, passwd, phone):
    line = f"{mail}:{passwd}:{phone}"
    await push_line_to_file(DONE_FILE, line)

async def append_error_line(email, password, phone):
    line = f"{email}:{password}:{phone}\n"
    async with file_lock:
        with open("error.txt", "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
    print(f"❌ Saved to error.txt: {email}:{password}:{phone}")

async def get_next_credentials():
    email_line = await pop_line_from_file(EMAILS_FILE)
    if email_line is None:
        return None
    phone_line = await pop_line_from_file(PHONES_FILE)
    if phone_line is None:
        async with file_lock:
            with open(EMAILS_FILE, "a", encoding="utf-8") as f:
                f.write(email_line + "\n")
        return None
    if ',' in email_line:
        mail, passwd = [p.strip() for p in email_line.split(",", 1)]
    else:
        mail, passwd = email_line.strip(), ""
    return mail, passwd, phone_line.strip()

# الآن: لو لقى نمط خطأ في الصفحة -> يحفظ و يرمي Exception فوراً
async def check_for_errors(page, email, password, phone, instance_id):
    error_patterns = [
        "Unexpected HTTP response: 503 Service Temporarily Unavailable",
        "Temporarily Unavailable",
        "This phone number cannot be used at this time",
        "-24054"
    ]
    for pattern in error_patterns:
        try:
            locator = page.locator(f"text={pattern}")
            if await locator.count() > 0 and await locator.is_visible():
                print(f"🛑 Error detected for {email}: {pattern}")
                await append_error_line(email, password, phone)
                raise Exception(f"Error detected: {pattern}")
        except Exception as e:
            # إذا كان هذا exception من append_error_line أو انتظار locator، أعد رفعه كـ خطأ حاسم
            if isinstance(e, Exception) and "Error detected" in str(e):
                raise
            # وإلا تجاوز (أو أعد رفع) حسب الموقف
            raise

# دوال click/fill/select معدلة لتتعامل كـ critical و ترمي Exception بعد الحفظ
async def click_button_by_css(page_or_frame, css_selector, nth_index=0, description="", wait_time=2, email=None, password=None, phone=None):
    try:
        button = page_or_frame.locator(css_selector).nth(nth_index)
        await button.wait_for(state="visible", timeout=15000)
        await button.click()
        print(f"✅ Clicked {description}")
        await asyncio.sleep(wait_time)
    except Exception as e:
        print(f"🛑 Critical: Failed to click {description}: {e}")
        if email:
            await append_error_line(email, password, phone)
            print(f"❌ Added to error.txt: {email}:{password}:{phone}")
        raise Exception(f"Failed critical step: click {description}")

async def fill_by_css(page_or_frame, css_selector, text, description="", wait_time=1, email=None, password=None, phone=None):
    try:
        elem = page_or_frame.locator(css_selector)
        await elem.wait_for(state="visible", timeout=15000)
        await elem.fill(text)
        print(f"✅ Filled {description} with '{text}'")
        await asyncio.sleep(wait_time)
    except Exception as e:
        print(f"🛑 Critical: Failed to fill {description}: {e}")
        if email:
            await append_error_line(email, password, phone)
            print(f"❌ Added to error.txt: {email}:{password}:{phone}")
        raise Exception(f"Failed critical step: fill {description}")

async def select_country(page_or_frame, dropdown_css, value="VN", email=None, password=None, phone=None):
    try:
        dropdown = page_or_frame.locator(dropdown_css)
        await dropdown.wait_for(state="visible", timeout=15000)
        await dropdown.select_option(value)
        print(f"✅ Selected country (value={value}) from dropdown")
        await asyncio.sleep(1)
    except Exception as e:
        print(f"🛑 Critical: Failed to select country: {e}")
        if email:
            await append_error_line(email, password, phone)
            print(f"❌ Added to error.txt: {email}:{password}:{phone}")
        raise Exception("Failed critical step: select country")

async def run_apple_login(instance_id, headless=False):
    while True:
        creds = await get_next_credentials()
        if creds is None:
            print(f"❌ No credentials/phone available for instance {instance_id}.")
            return
        EMAIL, PASSWORD, PHONE_NUMBER = creds
        print(f"🚀 Instance {instance_id} will use: {EMAIL} | {PHONE_NUMBER}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()
            try:
                await page.goto("https://account.apple.com/sign-in")
                await page.wait_for_timeout(3000)
                login_frame = page.frame_locator("iframe[src*='appleauth/auth/authorize/signin']")
                try:
                    await login_frame.locator("#account_name_text_field").fill(EMAIL)
                    await login_frame.locator("#sign-in").click()
                    await page.wait_for_timeout(2000)
                    await login_frame.locator("#password_text_field").fill(PASSWORD)
                    await login_frame.locator("#sign-in").click()
                    await page.wait_for_timeout(2000)
                except Exception as e:
                    # لو فشل login خطوة حساسة -> اعتبرها خطأ قاتل
                    print(f"🛑 Login step error: {e}")
                    await append_error_line(EMAIL, PASSWORD, PHONE_NUMBER)
                    raise Exception("Critical: login step failed")

                # فحص فوري للأخطاء النصية على الصفحة
                await check_for_errors(page, EMAIL, PASSWORD, PHONE_NUMBER, instance_id)

                # التعامل مع أسئلة الأمان
                try:
                    q_section_frame = page.frame_locator("iframe[src*='appleauth/auth/authorize/signin']")
                    q_section = q_section_frame.locator("text=Answer your security questions to continue.")
                    if await q_section.count() > 0 and await q_section.is_visible():
                        print(f"🛑 Security questions page detected for {EMAIL}")
                        unanswered = False

                        q1_elem = q_section_frame.locator("#question-1")
                        q2_elem = q_section_frame.locator("#question-2")

                        if await q1_elem.count() > 0:
                            q1 = (await q1_elem.text_content() or "").strip()
                            if q1 in answers_map:
                                await q_section_frame.locator("#question-1 + div input").fill(answers_map[q1])
                                print(f"✍️ Answered Q1: {q1} -> {answers_map[q1]}")
                            else:
                                unanswered = True

                        if await q2_elem.count() > 0:
                            q2 = (await q2_elem.text_content() or "").strip()
                            if q2 in answers_map:
                                await q_section_frame.locator("#question-2 + div input").fill(answers_map[q2])
                                print(f"✍️ Answered Q2: {q2} -> {answers_map[q2]}")
                            else:
                                unanswered = True

                        if unanswered:
                            await append_error_line(EMAIL, PASSWORD, PHONE_NUMBER)
                            raise Exception("Critical: Unknown security questions")

                        submit_btn = q_section_frame.locator("button[type='submit']:not([disabled])")
                        if await submit_btn.count() > 0:
                            await submit_btn.click()
                            print("✅ Submitted security answers")
                            await page.wait_for_timeout(7000)
                            still_on_questions = await q_section.count() > 0 and await q_section.is_visible()
                            if still_on_questions:
                                await append_error_line(EMAIL, PASSWORD, PHONE_NUMBER)
                                raise Exception("Critical: Still stuck on security questions")
                except Exception as e:
                    # رفع الاستثناء ليتم التقاطه في except العام أسفل
                    print(f"⚠️ Security-question handling error: {e}")
                    raise

                await check_for_errors(page, EMAIL, PASSWORD, PHONE_NUMBER, instance_id)

                frames = page.frames
                for f in [page] + frames:
                    try:
                        button = f.locator("text=Other Options")
                        if await button.count() > 0 and await button.is_visible():
                            await button.click()
                            print("✅ Clicked 'Other Options'")
                            await asyncio.sleep(2)
                            dont_upgrade = f.locator("text=Don't Upgrade")
                            for _ in range(10):
                                if await dont_upgrade.count() > 0 and await dont_upgrade.is_visible():
                                    await dont_upgrade.click()
                                    print("✅ Clicked 'Don't Upgrade'")
                                    break
                                await asyncio.sleep(5)
                            break
                    except:
                        continue

                # الآن: أي فشل هنا سيحفظ الحساب في error.txt ويقفل الـ instance
                await click_button_by_css(page, "button.button-bare.button-expand.button-rounded-rectangle", 2, "Account Security", email=EMAIL, password=PASSWORD, phone=PHONE_NUMBER)
                await click_button_by_css(page, "button.button-secondary.button-rounded-rectangle", 1, "Second option after Account Security", email=EMAIL, password=PASSWORD, phone=PHONE_NUMBER)
                await select_country(page, "select.form-dropdown-select", COUNTRY, email=EMAIL, password=PASSWORD, phone=PHONE_NUMBER)
                await fill_by_css(page, "input.form-textbox-input.form-textbox-input-ltr", PHONE_NUMBER, "phone number textbox", email=EMAIL, password=PASSWORD, phone=PHONE_NUMBER)

                phone_input = page.locator("input.form-textbox-input.form-textbox-input-ltr")
                try:
                    await phone_input.press("Enter")
                    print("✅ Pressed Enter to submit the phone number")
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"🛑 Couldn't press Enter: {e}")
                    await append_error_line(EMAIL, PASSWORD, PHONE_NUMBER)
                    raise Exception("Critical: couldn't press Enter on phone input")

                await check_for_errors(page, EMAIL, PASSWORD, PHONE_NUMBER, instance_id)

                print("📲 Starting verification code request loop...")
                while True:
                    try:
                        didnt_get = page.locator("button:has-text('Didn’t get a verification code?')")
                        send_new = page.locator("button:has-text('Send new code')")
                        if await didnt_get.count() > 0 and await didnt_get.is_visible():
                            await didnt_get.click()
                            print("✅ Clicked 'Didn’t get a verification code?'")
                            await asyncio.sleep(1.5)
                        if await send_new.count() > 0 and await send_new.is_visible():
                            await send_new.click()
                            print("✅ Clicked 'Send new code'")
                            await asyncio.sleep(1.5)
                        error_msg = page.locator("text=Too many verification codes have been sent")
                        if await error_msg.count() > 0 and await error_msg.is_visible():
                            print("🛑 Too many verification codes error detected.")
                            await append_error_line(EMAIL, PASSWORD, PHONE_NUMBER)
                            break
                        await check_for_errors(page, EMAIL, PASSWORD, PHONE_NUMBER, instance_id)
                    except Exception as e:
                        print(f"⚠️ Loop error: {e}")
                        # لو الخطأ داخل اللوب من النوع الحاسم نرميه للخارج ليغلق الـ browser
                        raise
                    await asyncio.sleep(5)

                await append_done_line(EMAIL, PASSWORD, PHONE_NUMBER)
                print(f"✅ Saved to {DONE_FILE}: {EMAIL}:{PASSWORD}:{PHONE_NUMBER}")

            except Exception as e:
                # أي استثناء هنا يعني فشل حاسم للـ instance — نضمن الحفظ لو ما تقمّش بالفعل
                try:
                    # محاولة لضمان أن الحساب محفوظ في error.txt
                    await append_error_line(EMAIL, PASSWORD, PHONE_NUMBER)
                except:
                    pass
                print(f"🛑 Instance {instance_id} stopped due to error: {e}")

            finally:
                try:
                    await browser.close()
                except Exception:
                    pass
                print(f"🛑 Browser instance {instance_id} closed.\n")

async def main():
    tasks = []
    for i in range(1, NUM_BROWSERS + 1):
        tasks.append(asyncio.create_task(run_apple_login(i, headless=not SHOWN)))
    if tasks:
        await asyncio.gather(*tasks)
    print("✅ All accounts finished. Exiting.")

if __name__ == "__main__":
    asyncio.run(main())
