import json, time, random, os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# === Tanya preferensi user ===
pakai_ua = input("Apakah mau pakai user-agent? (y/n): ").lower() == 'y'
pakai_proxy = input("Apakah mau pakai proxy? (y/n): ").lower() == 'y'

# === Load user-agent dan proxy jika diperlukan ===
if pakai_ua:
    with open("user-agent.json") as f:
        user_agents = json.load(f)
if pakai_proxy:
    with open("proxy.json") as f:
        proxies = json.load(f)

# === Input jumlah akun yang ingin digunakan ===
jumlah_akun = int(input("Berapa akun yang ingin digunakan?: "))

akun_list = []
for i in range(jumlah_akun):
    print(f"\nMasukkan cookie akun {i+1}:")
    cookie_str = input("> ").strip()

    # Simpan ke file JSON
    cookies_file = f"cookie{i+1}.json"

    # Convert string cookie (format: k=v; k2=v2; ...) ke list of dicts
    cookie_items = [x.strip() for x in cookie_str.split(";") if "=" in x]
    cookie_dict_list = []
    for item in cookie_items:
        k, v = item.split("=", 1)
        cookie_dict_list.append({
            "name": k,
            "value": v,
            "domain": ".twitter.com",
            "path": "/"
        })

    with open(cookies_file, "w") as f:
        json.dump(cookie_dict_list, f)

    print(f"✅ Cookie {i+1} berhasil disimpan.")
    akun_list.append({"username": f"akun{i+1}", "cookies": cookies_file})

# === Fungsi untuk load cookies ===
def load_cookies(driver, path):
    with open(path) as f:
        cookies = json.load(f)
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            pass  # beberapa cookie bisa gagal ditambahkan

# === Mulai proses auto-follow ===
for akun in akun_list:
    user_agent = random.choice(user_agents) if pakai_ua else None
    proxy = random.choice(proxies) if pakai_proxy else None

    options = uc.ChromeOptions()
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)

    try:
        driver.get("https://twitter.com/login")
        time.sleep(3)

        load_cookies(driver, akun["cookies"])
        driver.get("https://twitter.com/home")
        time.sleep(5)

        # Verifikasi login berhasil dengan buka profile settings
        try:
            driver.get("https://twitter.com/settings/profile")
            time.sleep(4)
            username_element = driver.find_element(By.XPATH, '//div[@data-testid="UserName"]')
            print(f"\n✅ Berhasil login sebagai: {username_element.text}")
        except:
            print("⚠️ Gagal mendeteksi username")

        # Input target follow
        target = input("Masukkan username yang ingin di-follow (tanpa @): ").strip()
        if not target:
            print("⚠️ Username kosong. Lewatkan.")
            driver.quit()
            continue

        driver.get(f"https://twitter.com/{target}")
        time.sleep(random.randint(4, 7))

        try:
            follow_btn = driver.find_element(By.XPATH, '//span[text()="Follow"]/ancestor::div[@role="button"]')
            follow_btn.click()
            print(f"🎯 Berhasil follow @{target} dengan akun {akun['username']}")
        except:
            print(f"⚠️ Gagal follow atau mungkin sudah follow @{target}")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        driver.quit()
        delay = random.randint(5, 9)
        print(f"\n⏳ Menunggu {delay} detik sebelum lanjut ke akun berikutnya...\n")
        for i in range(delay, 0, -1):
            print(f"{i}...", end='\r')
            time.sleep(1)