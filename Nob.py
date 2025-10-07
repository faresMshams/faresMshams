import asyncio, time, yaml
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
DONE_FILE = "Done.txt"
ERROR_FILE = "error.txt"

init(autoreset=True)
BANNER_COLOR = Fore.RED

banner = """
                        ██████╗ ██╗  ██╗ █████╗ ██╗     ██╗    ██╗ █████╗ ███████╗██╗  ██╗
                       ██╔════╝ ██║  ██║██╔══██╗██║     ██║    ██║██╔══██╗██╔════╝██║  ██║
                       ██║  ███╗███████║███████║██║     ██║ █╗ ██║███████║███████╗███████║
                       ██║   ██║██╔══██║██╔══██║██║     ██║███╗██║██╔══██║╚════██║██╔══██║
                       ╚██████╔╝██║  ██║██║  ██║███████╗╚███╔███╔╝██║  ██║███████║██║  ██║
                        ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                           No Proxy
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
    line = f"{email}:{password}:{phone}"
    await push_line_to_file(ERROR_FILE, line)
    print(f"❌ Saved to {ERROR_FILE}: {email}:{password}:{phone}")

async def click_button_by_css(page_or_frame, css_selector, nth_index=0, description="", wait_time=2):
    try:
        button = page_or_frame.locator(css_selector).nth(nth_index)
        await button.wait_for(state="visible", timeout=15000)
        await button.click()
        print(f"✅ Clicked {description}")
        await asyncio.sleep(wait_time)
    except Exception as e:
        print(f"⚠️ Failed to click {description}: {e}")

async def fill_by_css(page_or_frame, css_selector, text, description="", wait_time=1):
    try:
        elem = page_or_frame.locator(css_selector)
        await elem.wait_for(state="visible", timeout=15000)
        await elem.fill(text)
        print(f"✅ Filled {description} with '{text}'")
        await asyncio.sleep(wait_time)
    except Exception as e:
        print(f"⚠️ Failed to fill {description}: {e}")

async def select_country(page_or_frame, dropdown_css, value="VN"):
    try:
        dropdown = page_or_frame.locator(dropdown_css)
        await dropdown.wait_for(state="visible", timeout=15000)
        await dropdown.select_option(value)
        print(f"✅ Selected country (value={value}) from dropdown")
        await asyncio.sleep(1)
    except Exception as e:
        print(f"⚠️ Failed to select country: {e}")

# robust text search across context/pages/frames (fallback to html search)
async def find_text_in_context(context, text):
    try:
        # search in all pages and their frames
        for pg in list(context.pages):
            try:
                loc = pg.locator(f"text={text}")
                if await loc.count() > 0 and await loc.is_visible():
                    return True
            except Exception:
                pass
            try:
                for fr in pg.frames:
                    try:
                        locf = fr.locator(f"text={text}")
                        if await locf.count() > 0 and await locf.is_visible():
                            return True
                    except Exception:
                        pass
            except Exception:
                pass
        # fallback: search raw HTML of pages
        for pg in list(context.pages):
            try:
                html = await pg.content()
                if text in html:
                    return True
            except Exception:
                pass
    except Exception:
        pass
    return False

async def check_for_errors(context, page, email, password, phone):
    error_patterns = [
        "Unexpected HTTP response: 503 Service Temporarily Unavailable",
        "Temporarily Unavailable",
        "This phone number cannot be used at this time",
        "-24054"
    ]
    for pattern in error_patterns:
        found = await find_text_in_context(context, pattern)
        if found:
            print(f"🛑 Error detected for {email}: {pattern}")
            await append_error_line(email, password, phone)
            return True
    return False

async def check_login_failed_immediate(context, page, email, password, phone):
    text = "Failed to verify your identity. Try again."
    # ابحث في كل الإطارات والصفحة
    try:
        for pg in [page] + page.frames:
            try:
                if await pg.locator(f"text={text}").count() > 0:
                    print(f"🛑 Login failed detected for {email}.")
                    await append_error_line(email, password, phone)
                    return True
            except:
                continue
        # fallback: HTML
        htmls = [await page.content()]
        for fr in page.frames:
            try:
                htmls.append(await fr.content())
            except:
                continue
        for h in htmls:
            if text in h:
                print(f"🛑 Login failed detected for {email} (HTML search).")
                await append_error_line(email, password, phone)
                return True
    except:
        pass
    return False

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
                    await page.wait_for_timeout(7000)

                    # تحقق سريع من فشل تسجيل الدخول
                    login_failed = await check_login_failed_immediate(context, page, EMAIL, PASSWORD, PHONE_NUMBER)
                    if login_failed:
                        try: await browser.close()
                        except: pass
                        continue  # انتقل للحساب التالي فورًا

                except Exception as e:
                    print(f"⚠️ Login step error: {e}")
                    await append_error_line(EMAIL, PASSWORD, PHONE_NUMBER)
                    try: await browser.close()
                    except: pass
                    continue

                # تحقق من الأخطاء العامة (503 ... إلخ)
                if await check_for_errors(context, page, EMAIL, PASSWORD, PHONE_NUMBER):
                    try: await browser.close()
                    except: pass
                    continue

                # === التعامل مع صفحة Security Questions ===
                try:
                    q_section_frame = page.frame_locator("iframe[src*='appleauth/auth/authorize/signin']")
                    q_section = q_section_frame.locator("text=Answer your security questions to continue.")
                    if await q_section.count() > 0 and await q_section.is_visible():
                        print(f"🛑 Security questions page detected for {EMAIL}")
                        unanswered = False

                        # سؤال 1
                        q1_elem = q_section_frame.locator("#question-1")
                        try:
                            if await q1_elem.count() > 0:
                                await q1_elem.wait_for(state="visible", timeout=15000)
                                q1_text = (await q1_elem.text_content() or "").strip()
                                input1 = q_section_frame.locator("#question-1 + div input")
                                await input1.wait_for(state="visible", timeout=15000)
                                if q1_text in answers_map:
                                    await input1.fill(answers_map[q1_text])
                                    print(f"✍️ Answered Q1: {q1_text} -> {answers_map[q1_text]}")
                                else:
                                    print(f"❌ Unknown Q1: {q1_text}")
                                    unanswered = True
                        except Exception as e:
                            print(f"⚠️ Failed handling Q1: {e}")
                            unanswered = True

                        # سؤال 2
                        q2_elem = q_section_frame.locator("#question-2")
                        try:
                            if await q2_elem.count() > 0:
                                await q2_elem.wait_for(state="visible", timeout=15000)
                                q2_text = (await q2_elem.text_content() or "").strip()
                                input2 = q_section_frame.locator("#question-2 + div input")
                                await input2.wait_for(state="visible", timeout=15000)
                                if q2_text in answers_map:
                                    await input2.fill(answers_map[q2_text])
                                    print(f"✍️ Answered Q2: {q2_text} -> {answers_map[q2_text]}")
                                else:
                                    print(f"❌ Unknown Q2: {q2_text}")
                                    unanswered = True
                        except Exception as e:
                            print(f"⚠️ Failed handling Q2: {e}")
                            unanswered = True

                        if unanswered:
                            await append_error_line(EMAIL, PASSWORD, PHONE_NUMBER)
                            print(f"❌ Could not answer all security questions for {EMAIL}")
                            try: await browser.close()
                            except: pass
                            continue

                        # Submit
                        try:
                            submit_btn = q_section_frame.locator("button[type='submit']:not([disabled])")
                            if await submit_btn.count() > 0:
                                await submit_btn.wait_for(state="visible", timeout=15000)
                                await submit_btn.click()
                                print("✅ Submitted security answers")
                                await page.wait_for_timeout(10000)
                        except Exception as e:
                            print(f"⚠️ Failed to submit security answers: {e}")
                            await append_error_line(EMAIL, PASSWORD, PHONE_NUMBER)
                            try: await browser.close()
                            except: pass
                            continue

                        # تحقق إذا لسه على صفحة الأسئلة
                        still_on_questions = await q_section.count() > 0 and await q_section.is_visible()
                        if still_on_questions:
                            print("🛑 Still stuck on security questions after submitting answers.")
                            await append_error_line(EMAIL, PASSWORD, PHONE_NUMBER)
                            try: await browser.close()
                            except: pass
                            continue

                except Exception as e:
                    print(f"⚠️ Security-question handling error: {e}")
                    await append_error_line(EMAIL, PASSWORD, PHONE_NUMBER)
                    try: await browser.close()
                    except: pass
                    continue

                # === باقي التعامل مع الصفحة بعد تسجيل الدخول ===
                if await check_for_errors(context, page, EMAIL, PASSWORD, PHONE_NUMBER):
                    try: await browser.close()
                    except: pass
                    continue

                # Other Options / Don't Upgrade
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
                    except: continue

                # Account Security button (محاولة بدون توقف عند الفشل)
                await click_button_by_css(page, "button.button-bare.button-expand.button-rounded-rectangle", 2, "Account Security")
                await click_button_by_css(page, "button.button-secondary.button-rounded-rectangle", 1, "Second option after Account Security")

                # إدخال رقم الهاتف
                await select_country(page, "select.form-dropdown-select", COUNTRY)
                await fill_by_css(page, "input.form-textbox-input.form-textbox-input-ltr", PHONE_NUMBER, "phone number textbox")

                try:
                    phone_input = page.locator("input.form-textbox-input.form-textbox-input-ltr")
                    await phone_input.press("Enter")
                    print("✅ Pressed Enter to submit the phone number")
                    await asyncio.sleep(2)
                except Exception as e:
                    print(f"⚠️ Couldn't press Enter: {e}")

                # Verification code loop
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
                            break

                        if await check_for_errors(context, page, EMAIL, PASSWORD, PHONE_NUMBER):
                            break

                    except Exception as e:
                        print(f"⚠️ Loop error: {e}")
                    await asyncio.sleep(5)

                await append_done_line(EMAIL, PASSWORD, PHONE_NUMBER)
                print(f"✅ Saved to {DONE_FILE}: {EMAIL}:{PASSWORD}:{PHONE_NUMBER}")

            finally:
                try:
                    await browser.close()
                except: pass
                print(f"🛑 Browser instance {instance_id} closed.")

async def main():
    tasks = []
    for i in range(1, NUM_BROWSERS + 1):
        tasks.append(asyncio.create_task(run_apple_login(i, headless=not SHOWN)))
    if tasks:
        await asyncio.gather(*tasks)
    print("✅ All accounts finished. Exiting.")

if __name__ == "__main__":
    asyncio.run(main())
