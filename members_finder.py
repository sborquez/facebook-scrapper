# -*- coding: utf-8 -*-
"""
Created on Sat Jan 19 16:36:34 2019

@author: sborquez
"""
#%%
from scrapper import *

from tqdm import tqdm
from time import sleep

import argparse
import sys


DEBUG = True
SCROLL_PAUSE_TIME = 2

# Parse args
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--driver", required=False, help="Path to driver", default="webdriver/chromedriver.exe")
ap.add_argument("-j", "--json", required=False, help="Path to database file", default="db.json")
args = vars(ap.parse_args())

webdriver_path = args["driver"]
db_path = args["json"]

print(123)
#%%
#def main():
driver = load_driver(webdriver_path)
users_db = get_users_db(db_path)    

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
#group="FEUTFSM"
group=input("group link: https://www.facebook.com/groups/")
#users.update(set("group",[group])) # agrega el grupo a los usuario ya existentes en la base de datos
driver.get("https://www.facebook.com/groups/"+group+"/members/")

# find data from html
members_count = driver.find_element_by_xpath('//*[@id="groupsMemberBrowser"]/div[1]/div/div[1]/span').text
members_count = int(members_count.replace(".",""))
members_div = driver.find_element_by_id("groupsMemberSection_recently_joined")
members_list = members_div.find_element_by_class_name("fbProfileBrowserList")

# Prepare progress bar
total_errors = 0
total_added = len(users_db)
pbar = tqdm(total=members_count, initial=total_added)

# scroll down to member list
members_list.location_once_scrolled_into_view
first_ul = members_list.find_element_by_tag_name("ul")
add, err = get_users_from_ul(first_ul, group, users_db)
total_added += add
total_errors += err
# expanded lists added
lists = 0

# Infinite scrolling
# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")
prev_lists = []
#viewed_expanded_list
while True:
    # Scroll down to bottom
    for i in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
    del_elements(prev_lists, driver)
    
    # if new_height == last_height:
    #     break
    # last_height = new_height

    # find news lists loaded
    expanded_lists = members_list.find_elements_by_class_name("expandedList")
    #print("listas", len(expanded_lists))
    #lists += len(expanded_lists)
    for expanded_list in expanded_lists:
        ul = expanded_list.find_element_by_tag_name("ul")
        add, err = get_users_from_ul(ul, group, users_db)
        total_added += add
        total_errors += err
        pbar.update(add)
    prev_lists = expanded_lists

print(total_errors)

driver.close()
