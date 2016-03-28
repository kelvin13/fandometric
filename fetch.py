import time
from httplib2 import ServerNotFoundError
from tumblr_keys import client    #this imports the content in our tumblr_keys.py file

def yield_users(func, field, * args):
    count = 0
    offset = 0
    while True:
        try:
            blogs = func( * args, limit=20, offset=offset)
        except ServerNotFoundError:
            print('Server not found, trying again in 3 seconds')
            time.sleep(3)
            continue

        if field in blogs and blogs[field]:
            switch = 1
            for i in blogs[field]:
                count += 1
                print(str(count) + ".\t" + str(i["name"]))
                if i["name"] == "taylorswift":
                    print ("^^^TAYLORRRR!!!!")
                    time.sleep(3)
                yield i

            offset += 20

        elif "meta" in blogs and "status" in blogs["meta"]:
            if switch:
                print ("waiting on limits")
                switch = 0
        else:
            print ("end")
            break

def followers():
    return yield_users(client.followers, 'users', 'republicofswift')
def following():
    return yield_users(client.following, 'blogs')
