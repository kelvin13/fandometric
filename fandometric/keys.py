from . import pytumblr

with open('tumblr_keys.txt', 'rb') as K:
    _keys = [l.decode().strip() for l in K.readlines() if l][:4]

client = pytumblr.TumblrRestClient( * _keys )
