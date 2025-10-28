import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup

# --- Konfigurace ---
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")
WEB_URL = "https://www.pythonanywhere.com/user/planetum/consoles/latest/"


def zkontroluj_stranku_selenium():
    """Používá Selenium pro přihlášení a kontrolu obsahu."""
    
    print("Kontroluji webovou stránku pomocí Selenium...")
    
    # --- Nastavení Chrome Options pro Headless mód ---
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")         
    chrome_options.add_argument("--no-sandbox")            
    chrome_options.add_argument("--disable-dev-shm-usage") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-pipe") 
    chrome_options.add_argument("--window-size=1920,1080")
    
    # KLÍČOVÉ: Explicitní nastavení cesty k binárnímu souboru Chromium
    # Musí odpovídat cestě z YAML instalace
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    
    driver = None
    try:
        # Spuštění driveru s nastavenými options (spoléhá se na Selenium Manager)
        # Tímto krokem se zbavíme zasekávání
        driver = webdriver.Chrome(options=chrome_options) 
        driver.get(WEB_URL)
        
        print("Driver spuštěn, načítám stránku.")

        # --- Přihlášení (předpokládáme PythonAnywhere přihlašovací formulář) ---
        
        # Čekání na přihlašovací pole
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "auth-username"))
        )
        
        # Vyplnění a odeslání formuláře
        driver.find_element(By.NAME, "auth-username").send_keys(GMAIL_USER)
        driver.find_element(By.NAME, "auth-password").send_keys(GMAIL_PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        print("Přihlašovací údaje odeslány. Čekám na konzoli.")

        # --- Kontrola obsahu po přihlášení ---
        
        # Čekání, dokud se neobjeví prvek, který je specifický pro přihlášenou konzoli
        # Změňte 'console-title' na skutečný CSS selektor po přihlášení
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "console-container")) 
        )
        
        # Zde byste přidali logiku pro kontrolu skutečného obsahu,
        # který chcete na stránce ověřit.
        
        print(f"Úspěšně přihlášen a ověřen obsah stránky: {driver.title}")

    except Exception as e:
        print(f"Nastala chyba během Selenium operace: {e}")
    finally:
        if driver:
            driver.quit()
        print("Driver ukončen.")

# --- Hlavní spuštění ---
if __name__ == "__main__":
    if not GMAIL_USER or not GMAIL_PASSWORD:
        print("Chyba: Proměnné GMAIL_USER a GMAIL_PASSWORD nejsou nastaveny. Ukončuji.")
    else:
        zkontroluj_stranku_selenium()
