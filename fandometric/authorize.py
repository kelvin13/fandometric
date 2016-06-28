from .pytumblr import P_oauth2 as oauth
import hashlib
from urllib import parse
from .output import fail, bold, endc, succ

invert = '\033[7m'

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
    
    access_token = None
    print('Open this URL into your browser and authorize the application.\n')
    print(bold, 'http://www.tumblr.com/oauth/authorize?', content, endc, sep='')
    print("""
After authorizing this application, you’ll be redirected to your localhost domain. (Your browser will most likely not load the page.) Copy the 'oauth_verifier' value from the url in your browser’s navigation bar and paste it below. Do not include the '#_=_' at the end of the url. The 'oauth_verifier' value should look similar to the highlighted portion of the example below:

""", 'http://localhost/?oauth_token=0D8GYiSxDN2k0RBNqsNuEvniRt4Sgc51MSUKuCd6JWHAr8zTIk&oauth_verifier=', invert, 'jBM7p3fSDxbBgnH8YOL8t2TiggCjRrKiHrj2hqmFnYUkaiHlf7', endc, '#_=_', '\n', sep='')
    
    while access_token is None:
        verifier = input(succ + "oauth_verifier > " + endc)
        token.set_verifier(verifier)
        token_client = oauth.Client(consumer, token)
        _, token_content = token_client.request('http://www.tumblr.com/oauth/access_token', 'POST')
        token_content = token_content.decode()
        if token_content != 'Missing or invalid oauth_verifier.':
            access_token = dict(parse.parse_qsl(token_content))
            print()
        else:
            print('oauth_verifier invalid, try again...')
    
    

    print('Your access token        : %s' % access_token['oauth_token'])
    print('Your access token secret : %s' % access_token['oauth_token_secret'])

    _keys = ck, csd, access_token['oauth_token'], access_token['oauth_token_secret']

    with open('tumblr_keys.txt', 'w') as K:
        K.write('\n'.join(_keys))

    print()
    print(succ, bold, 'Authentication successful', endc, sep='')
    print()
