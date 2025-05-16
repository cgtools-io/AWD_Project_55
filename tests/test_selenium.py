import pytest, time
from selenium import webdriver
from tests.conftest import selenium_login
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import app.constants as msg

# LH = localhost base URL

def test_authenticated_pages_flow(selenium_driver, selenium_registered_user):
    # Log in helper
    selenium_login(selenium_driver, selenium_registered_user)

    # Dashboard             TODO: Delete if we're axing /dashboard
    # selenium_driver.get(msg.LH + "/dashboard")
    # assert "Your Total CGT" in selenium_driver.page_source

    #File Upload
    selenium_driver.get(msg.LH + "/file_upload")
    assert "Choose broker:" in selenium_driver.page_source

    # Share Data
    selenium_driver.get(msg.LH + "/share")
    assert "Shared with Me" in selenium_driver.page_source

    # Visuals (if any)
    selenium_driver.get(msg.LH + "/visual")
    assert "Real-time snapshot" in selenium_driver.page_source

    # Optional: Check nav bar or footer still visible
    assert "Logout" in selenium_driver.page_source
    
def test_file_upload(selenium_driver, selenium_registered_user):
    selenium_login(selenium_driver, selenium_registered_user)

    selenium_driver.get(msg.LH + "/file_upload/")
    assert "Choose broker:" in selenium_driver.page_source

    # Unhide the form section so Selenium can interact
    selenium_driver.execute_script("document.getElementById('form-first-part').style.display = 'block';")

    # Wait for the actual radio input
    # Click the img inside the label for the broker
    WebDriverWait(selenium_driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'img[alt="Binance"]'))
    ).click()

    # Confirm the input is selected after clicking the label
    radio = selenium_driver.find_element(By.ID, "broker-binance")
    assert radio.is_selected()