import os
import time
import smtplib
import traceback
from email.mime.text import MIMEText
from email.utils import formatdate
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ==================================
# ⚙️ NASTAVENÍ SKRIPTU
# ==================================
URL = "https://www.planetum.cz/porad/918-hurvinkova-vesmirna-odysea"
ODESILATEL = "chaloupecky.milan@gmail.com"
PRIJEMCE = "milan.chaloupecky@email.com"
HESLO = "frbcfizgpxjsrmzv"  # Gmail App Password (ne běžné heslo)
INTERVAL = 3600              # kontrola každou hodinu
TARGET_TEXT = "Prosinec 2025"


# ==================================
# 📧 FUNKCE NA ODESLÁNÍ EMAILU
# ==================================
def posli_email(predmet, zprava):
    """Odešle e-mail pomocí Gmailu (SMTP)."""
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
            print("✅ E-mail byl úspěšně odeslán.")
    except smtplib.SMTPAuthenticationError:
        print("❌ Chyba autentizace – zkontroluj App Password.")
    except Exception as e:
        print(f"❌ Chyba při odesílání e-mailu: {e}")
        traceback.print_exc()


# ==================================
# 🔎 FUNKCE NA KONTROLU STRÁNKY
# ==================================
def zkontroluj_stranku_selenium(url):
    """
    Načte stránku pomocí Selenium, hledá zadaný text a při nalezení pošle e-mail.
    """
    print(f"🔍 Kontroluji stránku: {url}")

    # Nastavení Chrome Options
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # ✅ Automatické stažení správného ChromeDriveru
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"❌ Chyba při spouštění ChromeDriveru: {e}")
        traceback.print_exc()
        return False

    try:
        driver.get(url)
        print("🌐 Stránka načtena, čekám na JavaScript...")
        time.sleep(5)

        page_text = driver.find_element(By.TAG_NAME, "body").text

        if TARGET_TEXT in page_text:
            print(f"🎯 Nalezen text '{TARGET_TEXT}'!")
            posli_email(
                f"Planetum.cz – nalezen text: {TARGET_TEXT}",
                f"Na stránce Planetum.cz byl nalezen text '{TARGET_TEXT}'.\n\n{url}"
            )
            return True
        else:
            print(f"🔎 Text '{TARGET_TEXT}' zatím nenalezen.")
            return False

    except Exception as e:
        print(f"❌ Chyba během kontroly stránky: {e}")
        traceback.print_exc()
        return False
    finally:
        driver.quit()
        print("🧹 ChromeDriver ukončen.")


# ==================================
# 🔁 HLAVNÍ SMYČKA
# ==================================
if __name__ == "__main__":
    print("▶️ Spouštím monitorovací skript pro Planetum.cz")
    while True:
        nalezeno = zkontroluj_stranku_selenium(URL)
        if nalezeno:
            print("✅ Podmínka splněna. Skript se ukončuje.")
            break

        print(f"⏳ Další kontrola za {INTERVAL / 60:.0f} minut...\n")
        time.sleep(INTERVAL)
