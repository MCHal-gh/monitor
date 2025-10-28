import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By

# ==================================
# ====== ⚙️ NASTAVENÍ SKRIPTU ======
# ==================================
URL = "https://www.planetum.cz/porad/918-hurvinkova-vesmirna-odysea"
PRIJEMCE = "milan.chaloupecky@email.com"
TARGET_TEXT = "Listopad 2025"             

# Načtení z Proměnných Prostředí (GitHub Secrets)
ODESILATEL = os.environ.get("GMAIL_USER")
HESLO = os.environ.get("GMAIL_PASSWORD")

# Načtení cest k prohlížeči a ovladači z YAML (Klíčové pro Možnost A!)
CHROME_PATH = os.environ.get("CHROME_PATH")
CHROME_DRIVER_PATH = os.environ.get("CHROME_DRIVER_PATH")

# =========================================
# ====== 📧 FUNKCE NA ODESLÁNÍ EMAILU ======
# =========================================
def posli_email(predmet, zprava):
    """Pokusí se odeslat e-mail přes Gmail SMTP s údaji z Secrets."""
    if not ODESILATEL or not HESLO:
        print("❌ Nelze odeslat e-mail: Chybí GMAIL_USER nebo GMAIL_PASSWORD.")
        return False
        
    # ... (zde je kód pro odeslání e-mailu – zůstává stejný) ...
    try:
        msg = MIMEText(zprava, 'plain', 'utf-8')
        msg["Subject"] = predmet
        msg["From"] = ODESILATEL
        msg["To"] = PRIJEMCE
        msg["Date"] = formatdate(localtime=True)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(ODESILATEL, HESLO)
            server.send_message(msg)
            print("✅ E-mail byl odeslán.")
            return True
    except Exception as e:
        print(f"❌ Chyba při odesílání e-mailu: {e}")
        return False

# =======================================
# ====== 🔎 FUNKCE NA KONTROLU STRÁNKY ======
# =======================================
def zkontroluj_stranku_selenium(url):
    """
    Stáhne stránku pomocí Headless Chrome, s dynamickou konfigurací cest.
    """
    print(f"Kontroluji {url} (Možnost A - Dynamické cesty)...")
    
    # --- Nastavení Chrome Options pro Headless mód ---
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")         
    chrome_options.add_argument("--no-sandbox")            
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-pipe") 
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Nastavení binární cesty POUZE POKUD ji Action předal
    if CHROME_PATH:
        chrome_options.binary_location = CHROME_PATH
    
    driver = None
    try:
        # POUŽITÍ SLUŽBY: Zde je klíč k úspěchu v Možnosti A
        if CHROME_DRIVER_PATH:
            service = webdriver.ChromeService(executable_path=CHROME_DRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
             # Fallback, pokud cesty nejsou k dispozici (měla by selhat)
             print("❌ CHYBA CESTY: Chybí CHROME_DRIVER_PATH. Spouštím bez explicitní cesty...")
             driver = webdriver.Chrome(options=chrome_options) 
        
        driver.set_page_load_timeout(45)
        
        driver.get(url)
        time.sleep(5) 
        
        page_text = driver.find_element(By.TAG_NAME, "body").text

        if TARGET_TEXT in page_text:
            print(f"🎯 Nalezen text '{TARGET_TEXT}'!")
            posli_email(
                f"Planetum – CÍL NALEZEN: {TARGET_TEXT}!",
                f"Na stránce {url} se objevil text '{TARGET_TEXT}'. Zarezervujte ihned!"
            )
            return True
        else:
            print(f"🔍 Zatím nic (text '{TARGET_TEXT}' nenalezen).")
            return False

    except Exception as e:
        print(f"❌ Došlo k chybě během Selenium operace: {e}")
        return False
    finally:
        if driver:
            driver.quit()

# ================================
# ====== 🔄 HLAVNÍ BLOK ======
# ================================
if __name__ == "__main__":
    
    if not ODESILATEL or not HESLO:
        print("❌ KRITICKÁ CHYBA: Chybí GMAIL_USER nebo GMAIL_PASSWORD v GitHub Secrets.")
        sys.exit(1)

    zkontroluj_stranku_selenium(URL)
