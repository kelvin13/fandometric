import time
from httplib2 import ServerNotFoundError

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
            for blog in blogs[field]:
                count += 1
                print(str(count) + '.\t' + str(blog['name']))
                if blog['name'] == 'taylorswift':
                    print ("^^^TAYLORRRR!!!!")
                    time.sleep(3)
                yield blog

            offset += 20

        elif 'meta' in blogs and 'status' in blogs['meta']:
            if switch:
                print ("waiting on limits")
                switch = 0
        else:
            print ('end')
            break
