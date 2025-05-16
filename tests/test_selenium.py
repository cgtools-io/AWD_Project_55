import pytest, time
from selenium import webdriver
from tests.conftest import selenium_login
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path

import app.constants as msg

# LH = localhost base URL




def test_authenticated_pages_flow(selenium_driver, selenium_registered_user):
    # Log in helper
    selenium_login(selenium_driver, selenium_registered_user)

    #File Upload
    selenium_driver.get(msg.LH + "/file_upload/")
    assert "Choose broker:" in selenium_driver.page_source

    # Share Data
    selenium_driver.get(msg.LH + "/share/")
    assert "Shared with Me" in selenium_driver.page_source

    # Visuals (if any)
    selenium_driver.get(msg.LH + "/visual/")
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

    file_input = selenium_driver.find_element(By.NAME, "file")
    file_input.send_keys(str(Path("tests/data/sample.csv").resolve()))

    # Submit the form
    submit_button = selenium_driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
    submit_button.click()

    # Wait for the result or flash message
    WebDriverWait(selenium_driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert"))
    )




def test_nav_links(selenium_driver, selenium_registered_user):
    selenium_login(selenium_driver, selenium_registered_user)

    # Navigate to home page to find the nav links
    selenium_driver.get(msg.LH + "/")
    
    nav_links = selenium_driver.find_elements(By.CSS_SELECTOR, "nav a")
    hrefs = [link.get_attribute("href") for link in nav_links if "/logout" not in link.get_attribute("href")]

    for href in hrefs:
        selenium_driver.get(href)
        assert "Page Not Found" not in selenium_driver.title



def test_two_users_can_share_the_good_good(selenium_driver, selenium_registered_user, selenium_dummy_user):
    selenium_login(selenium_driver, selenium_registered_user)

    selenium_driver.get(msg.LH + "/file_upload/")
    assert "Choose broker:" in selenium_driver.page_source

    # Unhide the form section so Selenium can interact
    selenium_driver.execute_script("document.getElementById('form-first-part').style.display = 'block';")

    WebDriverWait(selenium_driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'img[alt="Binance"]'))
    ).click()

    radio = selenium_driver.find_element(By.ID, "broker-binance")
    assert radio.is_selected()

    file_input = selenium_driver.find_element(By.NAME, "file")
    file_input.send_keys(str(Path("tests/data/sample.csv").resolve()))

    submit_button = selenium_driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
    submit_button.click()

    WebDriverWait(selenium_driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert"))
    )

    assert msg.UPLOAD_SUCCESS.lower() in selenium_driver.page_source.lower() or "upload successful!" in selenium_driver.page_source.lower()

