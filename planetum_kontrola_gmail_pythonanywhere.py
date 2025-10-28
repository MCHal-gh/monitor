from selenium import webdriver
from selenium.webdriver.chrome.options import Options # ⬅️ Opět používáme standardní Options
from selenium.webdriver.common.by import By
import smtplib
from email.mime.text import MIMEText
import time
from email.utils import formatdate

# ==================================
# ====== ⚙️ NASTAVENÍ SKRIPTU ======
# ==================================
URL = "https://www.planetum.cz/porad/918-hurvinkova-vesmirna-odysea"
ODESILATEL = "chaloupecky.milan@gmail.com"
PRIJEMCE = "milan.chaloupecky@email.com"
HESLO = "frbcfizgpxjsrmzv"
INTERVAL = 3600
TARGET_TEXT = "Prosinec 2025"

# =========================================
# ====== 📧 FUNKCE NA ODESLÁNÍ EMAILU ======
# ... (Zůstává stejná) ...
# =========================================
def posli_email(predmet, zprava):
    """Pokusí se odeslat e-mail přes Gmail SMTP."""
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
    except smtplib.SMTPAuthenticationError:
        print("❌ Chyba při odesílání e-mailu: Chyba autentizace (App Password).")
        print("   Zkontrolujte, zda je Heslo Aplikace správné.")
    except Exception as e:
        print(f"❌ Chyba při odesílání e-mailu: {e}")

# =======================================
# ====== 🔎 FUNKCE NA KONTROLU STRÁNKY ======
# =======================================
def zkontroluj_stranku_selenium(url):
    """
    Stáhne stránku pomocí Selenium Chrome Driveru s čistou konfigurací pro lokální běh.
    """
    print(f"Kontroluji {url} pomocí Selenium (Chrome - Lokální)...")
    
    # 1. Nastavení Chrome Options
    chrome_options = Options()
    
    # ❌ ÚPRAVA PRO LOKÁLNÍ BĚH: Odstranění konfigurace pro PythonAnywhere ❌
    # Nyní Selenium Manager najde vše samo.
    
    # Ostatní nastavení pro headless běh
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 3. Spuštění driveru
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"❌ Chyba při spouštění WebDriveru (Chrome): {e}")
        return False

    try:
        driver.get(url)
        time.sleep(5) # Čekání na spuštění JS

        page_text = driver.find_element(By.TAG_NAME, "body").text

        # 4. Kontrola textu
        if TARGET_TEXT in page_text:
            print(f"🎯 Nalezen text '{TARGET_TEXT}'!")
            
            posli_email(
                f"Planetum – nalezen {TARGET_TEXT}!",
                f"Na stránce Planetum.cz se objevil text '{TARGET_TEXT}'.\n\n{url}"
            )
            return True
        else:
            print(f"🔍 Zatím nic (text '{TARGET_TEXT}' nenalezen).")
            return False

    except Exception as e:
        print(f"❌ Došlo k chybě během načítání stránky: {e}")
        return False
    finally:
        driver.quit()

# ================================
# ====== 🔄 HLAVNÍ SMYČKA ======
# ================================
if __name__ == "__main__":
    print("▶️ Spouštím monitorovací skript Selenium...")
    
    while True:
        if zkontroluj_stranku_selenium(URL): 
            print("\n✅ Podmínka splněna. Program se ukončuje.")
            break 
        
        print(f"⏳ Další kontrola za {INTERVAL/60:.0f} minut (v {INTERVAL} sekundách)...\n")
        time.sleep(INTERVAL)