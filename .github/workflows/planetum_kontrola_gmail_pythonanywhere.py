import os
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Konfigurace ---
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")
WEB_URL = "https://www.pythonanywhere.com/user/planetum/consoles/latest/"

def zkontroluj_stranku_selenium():
    """Používá Selenium pro přihlášení a kontrolu obsahu."""
    print("Kontroluji webovou stránku pomocí Selenium...")

    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-pipe")
    chrome_options.add_argument("--window-size=1920,1080")

    # Optional: povolit přepsání přes env, jinak NEPŘEPIŠ (Selenium Manager si poradí)
    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin:
        print(f"Používám CHROME_BIN z env: {chrome_bin}")
        chrome_options.binary_location = chrome_bin
    else:
        print("CHROME_BIN není nastaven. Nezadávám binary_location a spoléhám na Selenium Manager / systém.")

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)  # Selenium Manager se postará o driver
        driver.get(WEB_URL)
        print("Driver spuštěn, načítám stránku:", WEB_URL)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "auth-username"))
        )

        driver.find_element(By.NAME, "auth-username").send_keys(GMAIL_USER or "")
        driver.find_element(By.NAME, "auth-password").send_keys(GMAIL_PASSWORD or "")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        print("Přihlašovací údaje odeslány. Čekám na konzoli...")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "console-container"))
        )

        print(f"Úspěšně přihlášen a ověřen obsah stránky: {driver.title}")

    except Exception as e:
        print("Nastala chyba během Selenium operace:")
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
        print("Driver ukončen.")

if __name__ == "__main__":
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print("Chyba: Proměnné GMAIL_USER a GMAIL_PASSWORD nejsou nastaveny. Ukončuji.")
    else:
        zkontroluj_stranku_selenium()
