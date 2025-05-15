# tests/selenium/test_login_ui.py

import pytest, time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import app.constants as msg

def test_login_page_loads(selenium_driver):
    driver = selenium_driver

    driver.get("http://localhost:5000/login")
    assert "Login" in driver.title
    assert driver.find_element(By.NAME, "username")
    assert driver.find_element(By.NAME, "password")

def test_login_page_logs_in(selenium_driver):
    driver = selenium_driver
    
    driver.get("http://localhost:5000/login")

    username = driver.find_element(By.NAME, "username")
    password = driver.find_element(By.NAME, "password")

    username.send_keys(msg.TEST_USER)
    password.send_keys(msg.TEST_PASSWORD)
    password.send_keys(Keys.RETURN)

    time.sleep(1)

    assert "Logout" in driver.page_source

def test_register_then_login(selenium_driver):
    driver = selenium_driver
    base_url = "http://localhost:5000"

    #Goes to signup page
    driver.get(f"{base_url}/signup")

    #Fills and then submit signup form
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(msg.TEST_USER)
    driver.find_element(By.NAME, "email").send_keys(msg.TEST_EMAIL)
    driver.find_element(By.NAME, "password").send_keys(msg.TEST_PASSWORD)
    driver.find_element(By.NAME, "confirm_password").send_keys(msg.TEST_PASSWORD)
    driver.find_element(By.NAME, "submit").click()

    # then log out if automatically logged in
    driver.get(f"{base_url}/logout")

    # Go to login page
    driver.get(f"{base_url}/login")

    # fill and submit the login form
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "username")))
    driver.find_element(By.NAME, "username").send_keys(msg.TEST_USER)
    driver.find_element(By.NAME, "password").send_keys(msg.TEST_PASSWORD)
    driver.find_element(By.NAME, "submit").click()

    #  assert that login was successful
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    assert "Logout" in driver.page_source