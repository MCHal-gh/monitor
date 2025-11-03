import os
import time
import smtplib
import traceback
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import formatdate
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# ==================================
# ⚙️ NASTAVENÍ SKRIPTU
# ==================================
URL = "https://www.planetum.cz/porad/918-hurvinkova-vesmirna-odysea"
TARGET_TEXT = "Prosinec 2025"

# Gmail údaje načítané z GitHub Secrets
ODESILATEL = os.environ.get("GMAIL_USER")
HESLO = os.environ.get("GMAIL_APP_PASSWORD")
PRIJEMCE = "milan.chaloupecky@email.com"
INTERVAL = 3300  # kontrola každou hodinu

# ==================================
# 📧 Funkce pro odeslání e-mailu
# ==================================
def posli_email(predmet, zprava):
    try:
        msg = MIMEText(zprava, "plain", "utf-8")
        msg["Subject"] = predmet
        msg["From"] = ODESILATEL
        msg["To"] = PRIJEMCE
        msg["Date"] = formatdate(localtime=True)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(ODESILATEL, HESLO)
            server.send_message(msg)
            print("✅ E-mail byl odeslán.")
    except smtplib.SMTPAuthenticationError:
        print("❌ Chyba autentizace – zkontrolujte App Password.")
    except Exception as e:
        print(f"❌ Chyba při odesílání e-mailu: {e}")
        traceback.print_exc()

# ==================================
# 🔎 Funkce pro kontrolu stránky
# ==================================
def zkontroluj_stranku_selenium(url):
    print(f"🔍 Kontroluji {url} pomocí Selenium...")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        time.sleep(5)  # krátká pauza pro načtení JS
        page_text = driver.find_element(By.TAG_NAME, "body").text

        if TARGET_TEXT in page_text:
            print(f"🎯 Nalezen text '{TARGET_TEXT}'!")
            posli_email(
                f"Planetum.cz – nalezen '{TARGET_TEXT}'!",
                f"Na stránce Planetum.cz byl nalezen text '{TARGET_TEXT}'.\n\n{url}"
            )
            return True
        else:
            print(f"🔍 Zatím nic (text '{TARGET_TEXT}' nenalezen).")
            return False

    except Exception as e:
        print("❌ Chyba během kontroly stránky:")
        traceback.print_exc()
        return False
    finally:
        if driver:
            driver.quit()
        print("🧹 ChromeDriver ukončen.")

# ==================================
# 🕒 Hlavní běh
# ==================================
if __name__ == "__main__":
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"▶️ Spouštím monitorovací skript Planetum.cz v {start_time} (UTC).")

    if not ODESILATEL or not HESLO:
        print("❌ Proměnné GMAIL_USER a GMAIL_APP_PASSWORD nejsou nastaveny. Ukončuji.")
    else:
        success = zkontroluj_stranku_selenium(URL)
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if success:
            print(f"✅ Podmínka splněna – skript se ukončuje ({end_time} UTC).")
        else:
            print(f"✅ Skript dokončen bez nálezu ({end_time} UTC).")
