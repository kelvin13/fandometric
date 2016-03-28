import time, datetime
import fetch
import jamestaylor

followers = [U['name'] + '|' + str(U['updated']) for U in fetch.followers()]
following = [U['name'] + '|' + str(U['updated']) for U in fetch.following()]

jamestaylor.write_record(time.time(), followers, following)
