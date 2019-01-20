# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 16:36:34 2019

@author: sborquez
"""
#%%
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from time import sleep

from tinydb import TinyDB, Query
from tinydb.operations import delete, add

from tqdm import tqdm

import getpass
from os import path
import sys

import argparse

DEBUG = True
SCROLL_PAUSE_TIME = 3

# Parse args
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--driver", required=False, help="Path to driver", default="webdriver/chromedriver.exe")
ap.add_argument("-j", "--json", required=False, help="Path to database file", default="db.json")
args = vars(ap.parse_args())

webdriver_path = args["driver"]
schedule_db_path = args["json"]

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

#%%
def get_users_db():
    db = TinyDB(schedule_db_path)
    users_db = db.table("users")
    return users_db            

def get_users_from_ul(ul_element, group, users_db, print_=False):
    users = ul_element.find_elements_by_tag_name("div")
    added = 0
    for user_div in users:
        try:
            user_a = user_div.find_element_by_xpath("./div/div[2]/div/div[2]/div[1]/a")
            name = user_a.text
            if "profile.php?id" in user_a.get_attribute("href"):
                link =  user_a.get_attribute("href").split("&")[0]
                user_id = link.split("=")[1]
            else:
                link = user_a.get_attribute("href").split("?")[0]
                user_id = link.split("/")[-1]

            if len(users_db.search(Query().user_id == user_id)) == 0:
                users_db.insert({"user":user_id, "name": name, "link": link, "groups":[group]})
                added += 1
                if print_:
                    print("[",str(added),"] Added:", user_id)
        
        except Exception as e:
            with open("error.log", "a") as log:
                log.write("Error adding {user_id}\{e}\n".format(user_id=user_id, e=e))

    return added
#%%
#def main():
if not path.exists(webdriver_path):
    print("No existe el archivo", webdriver_path)
    exit(1)

if "chromedriver" in path.basename(webdriver_path):
    driver = webdriver.Chrome(webdriver_path)
else:
    driver = webdriver.Firefox(webdriver_path)

users_db = get_users_db()    

# Open webdriver
#driver = webdriver.Firefox(webdriver_path)
driver.get("https://www.facebook.com/")

# Try to log in
if is_logged(driver) and not DEBUG:
    # TODO cerrar sesion  
    print("closing previous session")
    logout()
loggin(driver)


# Select source group 
group="FEUTFSM"
#group=input("group link: https://www.facebook.com/groups/")
#users.update(set("group",[group])) # agrega el grupo a los usuario ya existentes en la base de datos
driver.get("https://www.facebook.com/groups/"+group+"/members/")

# find data from html
members_count = driver.find_element_by_xpath('//*[@id="groupsMemberBrowser"]/div[1]/div/div[1]/span').text
members_count = int(members_count.replace(".",""))
#members_count = int(driver.find_element_by_class_name("_grt _50f8").text)
members_div = driver.find_element_by_id("groupsMemberSection_recently_joined")
members_list = members_div.find_element_by_class_name("fbProfileBrowserList")

# Prepare progress bar
total_added = len(users_db)
pbar = tqdm(total=members_count, initial=total_added)

# scroll down to member list
members_list.location_once_scrolled_into_view
first_ul = members_list.find_element_by_tag_name("ul")
total_added += get_users_from_ul(first_ul, group, users_db)

# expanded lists added
lists = 0

# Infinite scrolling
# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    # if new_height == last_height:
    #     break
    # last_height = new_height

    # find news lists loaded
    expanded_lists = members_list.find_elements_by_class_name("expandedList")[lists:]
    lists += len(expanded_lists)
    for expanded_list in expanded_lists:
        ul = expanded_list.find_element_by_tag_name("ul")
        total_added += get_users_from_ul(ul, group, users_db)
        pbar.update(total_added)

    

#driver.close()
    
#%%
#main()

#%%
#if __name__ == "__main__":
#    main()

