from tinydb import TinyDB, Query
from tinydb.operations import delete, add, set

SKIP=True
#%%
def get_users_db(db_path):
    db = TinyDB(db_path)
    users_db = db.table("users")
    return users_db            

def get_users_from_ul(ul_element, group, users_db, print_=False):
    users = ul_element.find_elements_by_tag_name("div")
    added = 0
    errors = 0
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

            if SKIP or len(users_db.search(Query().user_id == user_id)) == 0:
                users_db.insert({"user":user_id, "name": name, "link": link, "groups":[group]})
                added += 1
                if print_:
                    print("[",str(added),"] Added:", user_id)
        
        except Exception as e:
            errors += 1
            with open("error.log", "a") as log:
                log.write("Error adding {user_id}\{e}\n".format(user_id=user_id, e=e))

    return added, errors
