from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import getpass
from os import path


def load_driver(webdriver_path):
    if not path.exists(webdriver_path):
        print("No existe el archivo", webdriver_path)
        exit(1)
    if "chromedriver" in path.basename(webdriver_path):
        driver = webdriver.Chrome(webdriver_path)
    else:
        driver = webdriver.Firefox(webdriver_path)
    return driver

def is_logged(driver):
    try:
        driver.find_element_by_id("email")
    except NoSuchElementException:
        return True
    else:
        return False

def __get_login_credentials():
    _email = input("email: ")
    _password = getpass.getpass("password: ")
    return _email, _password

def __login(driver):
    _email, _password = __get_login_credentials()
    driver.find_element_by_id("email").send_keys(_email)
    driver.find_element_by_id("pass").send_keys(_password)
    driver.find_element_by_id("loginbutton").click()
    
def loggin(driver):
    __login(driver)
    while "https://www.facebook.com/login/" in driver.current_url:
        print("email or password is incorrect. Try again.")
        __login(driver)
    
def logout():
    pass

def del_elements(elements, driver):
    try:
        for element in elements:
            driver.execute_script("var element = arguments[0]; element.parentNode.removeChild(element);", element)
    except Exception as e:
        print(e)