from time import time
from itertools import chain

from .fetch import yield_users, attempt_api_call
from .archivist import User_group
from . import keys

import ui

def _get_users(url, out, celeb=None, ** kwargs):
    out(new='blog fetch')
    search_status = celeb is None
    if not search_status:
        out({'search_name': celeb})
    
    # get totals
    if type(url) is tuple:
        total = kwargs['following']
        progress_string = ('Downloading blog ({0} of {1}) followed by primary <' + url[0] + '> ').format
        url = None
    else:
        total = attempt_api_call(out, keys.client.followers, url, limit=0)['total_users']
        progress_string = ('Downloading followers ({0} of {1}) on <' + url + '> ').format
    
    n = 0
    working = ui.Colors.WORKING
    warning = ui.Colors.WARNING
    def emit_progress_string(n, total): 
        try:
            percent = n/total * 100
        except ZeroDivisionError:
            percent = 100
        out({'color': working, 'msg': progress_string(n, total), 'percent': percent})
    
    was_msg = False
    for U in yield_users(url):
        if type(U) is str:
            out({'color': warning, 'msg': U + ' '})
            was_msg = True
        else:
            if not search_status and U['name'] == celeb:
                search_status = True
                out({'search_found': True})
            
            n += 1
            yield U
            if not n % 10 or was_msg:
                emit_progress_string(n, total)
                was_msg = False
    emit_progress_string(n, total)
    ui.sleep(0.001)

def update(urls, directory='records', out=print, ** kwargs ):
    out('Connecting to tumblr...')
    
    ui.sleep(0.001)
    # check that the url is owned by the client
    userinfo = attempt_api_call(out, keys.client.info)['user']
    blogs    = userinfo['blogs']
    primary  = next(blog['name'] for blog in blogs if blog['primary'])
    owned    = {blog['name'] for blog in blogs}
    invalid  = set(u[0] for u in urls) - owned
    if invalid:
        if len(invalid) == 1:
            msg = 'blog <{0}> is not owned by primary <{1}>'.format(next(iter(invalid)), primary)
        else:
            msg = 'blogs {0} are not owned by primary <{1}>'.format(', '.join('<' + url + '>' for url in sorted(invalid)), primary)
        raise ui.FandomError(msg)
    
    outgoing   = ((primary, 'following'), {'following': userinfo['following']}),
    usergroups = ((url, _get_users(url, out, ** options )) for url, options in chain(urls, outgoing))
    snapshot   = User_group.from_blogs(time(), usergroups)
    
    snapshot.save(directory)

def _parse_options(options, shorts={}):
    for option in options:
        if option[:2] == '--':
            if '=' in option:
                yield option[2:].split('=')
            else:
                yield option[2:], True
        elif option[0] == '-':
            yield from ((shorts[letter], True) for letter in option[1:] if letter in shorts)
        else:
            yield option

def _into_groups(args, look_for=frozenset()):
    url_groups = []
    free_args  = {}
    for arg in args:
        if type(arg) is str:
            url_groups.append((arg, {}))
        else:
            option, value = arg
            if option in look_for:
                try:
                    url_groups[-1][1][option] = value
                except IndexError:
                    raise ui.FandomError('option [{0}] not bound to any url')
            else:
                free_args[option] = value

    return url_groups, free_args

def _reconstitute(url_groups):
    for url, D in url_groups:
        yield url
        for opt, v in D.items():
            if type(v) is str:
                yield '--' + opt + '=' + v
            else:
                yield '--' + opt

def update_c(commands, out):
    url_groups, free_args = _into_groups(_parse_options(commands, shorts={'c': 'cache'}), look_for={'celeb'})
    if 'cache' in free_args:
        argstr = ' '.join(_reconstitute(url_groups))
        with open('terminal.txt', 'w') as T:
            T.write(argstr)
    update(tuple((url.lstrip('@'), D) for url, D in url_groups), out=out, ** free_args )
