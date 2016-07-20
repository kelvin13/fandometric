from .pytumblr import P_oauth2 as oauth
import hashlib
from urllib import parse
from .output import fail, bold, endc, succ
from .receiver import build_receiver

import webbrowser

def generate_key(password):
    return hashlib.sha224(password.encode()).hexdigest()

def encode(password, string):
    key = generate_key(password)
    return [ord(string[i]) + ord(key[i % len(key)]) for i in range(len(string))]

def decode(password, L):
    key = generate_key(password)
    return ''.join(map(chr, (L[i] - ord(key[i % len(key)]) for i in range(len(L)))))

ck = '92y6yT6shCLPBE02KjlrBa6Y7Ab9NGsX68MCqamG5AhKAsBK0E'
cs = [212, 151, 106, 211, 151, 166, 130, 123, 160, 165, 152, 202, 125, 118, 105, 213, 213, 133, 184, 157, 128, 171, 174, 150, 128, 214, 121, 122, 132, 115, 194, 165, 139, 167, 135, 209, 99, 220, 122, 174, 167, 174, 213, 181, 215, 216, 207, 198, 158, 213]

def setup():
    print("""
Fandometric needs your tumblr keys in order to access your followers and following lists. You will only need to do this once. You can revoke its access at any time by going to Tumblr Settings > Apps on tumblr.com. 
""")

    request_token = None
    while request_token is None:
        password = input(succ + "fandometric passkey > " + endc)
        csd = decode(password, cs)

        consumer = oauth.Consumer(ck, csd)
        client = oauth.Client(consumer)

        _, content = client.request('http://www.tumblr.com/oauth/request_token', 'POST')
        content = content.decode()
        if content != 'oauth_signature does not match expected value':
            request_token = dict(parse.parse_qsl(content))
            print()
        else:
            print('passkey invalid, try again...')
    
    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])

    webbrowser.open(url='http://www.tumblr.com/oauth/authorize?' + content)
    
    localhost = build_receiver(consumer, token, ck, csd)
    localhost.run(port=1989)
    


