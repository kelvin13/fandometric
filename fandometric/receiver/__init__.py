import logging

from fandometric.pytumblr import P_oauth2 as oauth
from fandometric.output import fail, bold, endc, succ

from urllib import parse

from .page import page

from flask import Flask, request, send_from_directory

def shutdown_receiver():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
def build_receiver(consumer, token, ck, csd):
    localhost = Flask(__name__)
    
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    @localhost.route('/<path:path>')
    def send_css(path):
        return send_from_directory('static', path)
    
    @localhost.route("/")
    def receive():
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

        print(succ, bold, 'Authentication successful', endc, sep='')
        print('Press [Ctrl-C] to continue', end='\n\n')
        
        return page.format( ** access_token )
    
    return localhost
