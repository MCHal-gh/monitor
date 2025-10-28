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
PRIJEMCE = "milan.chaloupecky@email.com"  # E-mail, kam má přijít upozornění
TARGET_TEXT = "Listopad 2025"             # Cílový text, který hledáte

# 🌟 DŮLEŽITÉ: Načtení z Proměnných Prostředí (GitHub Secrets)
# Tyto názvy musí přesně odpovídat názvům v YAML souboru a v GitHub Secrets!
ODESILATEL = os.environ.get("GMAIL_USER")
HESLO = os.environ.get("GMAIL_PASSWORD")

# =========================================
# ====== 📧 FUNKCE NA ODESLÁNÍ EMAILU ======
# =========================================
def posli_email(predmet, zprava):
    """Pokusí se odeslat e-mail přes Gmail SMTP s údaji z Secrets."""
    if not ODESILATEL or not HESLO:
        print("❌ Nelze odeslat e-mail: Chybí GMAIL_USER nebo GMAIL_PASSWORD.")
        return False
        
    try:
        msg = MIMEText(zprava, 'plain', 'utf-8')
        msg["Subject"] = predmet
        msg["From"] = ODESILATEL
        msg["To"] = PRIJEMCE
        msg["Date"] = formatdate(localtime=True)

        # Standardní nastavení pro Gmail
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
    Stáhne stránku pomocí Headless Chrome, konfigurovaného pro Linux server.
    """
    print(f"Kontroluji {url} pomocí Selenium (Headless Chrome na GitHub Actions)...")
    
    # --- Nastavení Chrome Options pro Headless mód na Linuxu ---
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")              # Běží bez grafického rozhraní
    chrome_options.add_argument("--no-sandbox")             # Důležité pro cloudové servery
    chrome_options.add_argument("--disable-dev-shm-usage")  # Zabraňuje problémům s pamětí
    
    # Cesta k Chromium nainstalovanému pomocí apt-get
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    # --- Konec nastavení ---
    
    driver = None
    try:
        # Spuštění driveru s nastavenými options
        driver = webdriver.Chrome(options=chrome_options)
        
        driver.get(url)
        time.sleep(5)  # Dáme čas na načtení JavaScriptu
        
        # Získání celého obsahu stránky
        page_text = driver.find_element(By.TAG_NAME, "body").text

        # Kontrola textu
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
# ====== 🔄 HLAVNÍ BLOK (Spustí se jen jednou) ======
# ================================
if __name__ == "__main__":
    
    # Kontrola kritických Secrets hned na začátku
    if not ODESILATEL or not HESLO:
        print("❌ KRITICKÁ CHYBA: Chybí GMAIL_USER nebo GMAIL_PASSWORD v GitHub Secrets.")
        print("   Zkontrolujte, zda jsou Secrets nastaveny a názvy sedí.")
        sys.exit(1)

    print("▶️ Spouštím monitorovací skript Selenium (GitHub Actions)...")
    
    # Skript se spustí a ihned skončí (čekání na další Cron job)
    zkontroluj_stranku_selenium(URL)
