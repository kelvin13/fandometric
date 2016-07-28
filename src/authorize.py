from .pytumblr import P_oauth2 as oauth
from urllib import parse
from flask import request, render_template

from . import keys
from .keygen import decode

import webbrowser

ck = '92y6yT6shCLPBE02KjlrBa6Y7Ab9NGsX68MCqamG5AhKAsBK0E'
cs = [163, 152, 107, 168, 146, 217, 171, 172, 209, 160, 99, 162, 168, 121, 152, 211, 162, 174, 136, 199, 124, 172, 171, 98, 133, 213, 172, 125, 132, 121, 151, 211, 145, 117, 134, 165, 103, 175, 165, 175, 161, 124, 168, 176, 215, 167, 158, 154, 151, 216]

_KEY_STATE = [None, None, ck, None]

def setup(password):
    csd = decode(password, cs)
    
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
