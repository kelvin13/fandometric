from .pytumblr import P_oauth2 as oauth
import hashlib
from urllib import parse

from . import keys
from flask import request, render_template

import webbrowser

def generate_key(password):
    return hashlib.sha224(password.encode()).hexdigest()

def _encode(password, string):
    key = generate_key(password)
    return [ord(string[i]) + ord(key[i % len(key)]) for i in range(len(string))]

def _decode(password, L):
    key = generate_key(password)
    return ''.join(map(chr, (L[i] - ord(key[i % len(key)]) for i in range(len(L)))))

ck = '92y6yT6shCLPBE02KjlrBa6Y7Ab9NGsX68MCqamG5AhKAsBK0E'
cs = [212, 151, 106, 211, 151, 166, 130, 123, 160, 165, 152, 202, 125, 118, 105, 213, 213, 133, 184, 157, 128, 171, 174, 150, 128, 214, 121, 122, 132, 115, 194, 165, 139, 167, 135, 209, 99, 220, 122, 174, 167, 174, 213, 181, 215, 216, 207, 198, 158, 213]

_KEY_STATE = [None, None, ck, None]

def setup(password):
    csd = _decode(password, cs)
    
    consumer = oauth.Consumer(ck, csd)
    client = oauth.Client(consumer)

    _, content = client.request('http://www.tumblr.com/oauth/request_token', 'POST')
    content = content.decode()
    if content == 'oauth_signature does not match expected value':
        return False
    
    request_token = dict(parse.parse_qsl(content))
    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    
    webbrowser.open(url='http://www.tumblr.com/oauth/authorize?' + content)
    _KEY_STATE[:] = [consumer, token, ck, csd]
    return True
    
def build_key_receiver(localhost):
    @localhost.route("/authorized")
    def receive():
        consumer, token, ck, csd = _KEY_STATE
        verifier = request.args.get('oauth_verifier')
        
        token.set_verifier(verifier)
        token_client = oauth.Client(consumer, token)
        _, token_content = token_client.request('http://www.tumblr.com/oauth/access_token', 'POST')
        token_content = token_content.decode()
        if token_content != 'Missing or invalid oauth_verifier.':
            access_token = dict(parse.parse_qsl(token_content))
        else:
            raise RuntimeError('fatal: oauth_verifier invalid')

        _keys = ck, csd, access_token['oauth_token'], access_token['oauth_token_secret']
        
        with open('tumblr_keys.txt', 'w') as K:
            K.write('\n'.join(_keys))
        keys.client = keys.make_client()
        print('Authentication successful')
        
        return render_template('authorized.html', ** access_token )
