from itertools import chain

import os

from _version import __version__

from .ui import FandomError

def max_file_index(directory):
    try:
        files = next(os.walk(directory))[2]
        return max(int(os.path.splitext(name)[0]) for name in next(os.walk(directory))[2])
    except (StopIteration, ValueError):
        return 0

def _users_to_tuple(users):
    return tuple((U['name'], U['updated']) for U in users)

def _users_serialize(users):
    return '\n'.join(U[0] + '|' + str(U[1]) for U in users)

def _find_table(tables, table):
    return next(entry for key, entry in tables if key == table)

def _interpret_header(tables, prefix):
    plen = len(prefix)
    for table, content in tables:
        if table[:plen] == prefix:
            url = table[plen:]
            if '/' in url:
                url, * components = url.split('/')
                if components[0] == 'following':
                    url = (url, 'following')
            yield url, tuple((U, int(T)) for U, T in (blog.split('|') for blog in content.split()))
    
class User_group(object):
    min_version = ['2']
    def __init__(self, timestamp, usergroups):
        self.timestamp  = timestamp
        self.fsets      = followersets = {}
        self._UGS       = UGS          = {}
        self._members   = members      = []
        self.primary    = None
        for url, users in usergroups:
            if type(url) is tuple:
                key = '/'.join(url)
                UGS[key] = users
                self.gset     = frozenset(U[0] for U in users)
                self.primary  = url[0]
                self.gkey     = key
            else:
                UGS[url]          = users
                followersets[url] = frozenset(U[0] for U in users)
                members.append(url)
    
    @classmethod
    def from_blogs(cls, timestamp, usergroups):
        return cls(timestamp, ((url, _users_to_tuple(users)) for url, users in usergroups))
    
    @classmethod
    def from_file(cls, F):
        tables = tuple(table.split(':::') for table in F.read().split('@'))
        info   = {'__version__': '1.1', '__time__': '0'}
        try:
            tinfo = next(v for k, v in tables if k == '__info__')
            info.update(p for p in (pair.split('=') for pair in tinfo.split('\n') if pair) if len(p) == 2)
        except StopIteration:
            pass
        else:
            version = info['__version__'].split('.')
            if cls.min_version <= version <= __version__:
                return cls(float(info['__time__']), _interpret_header(tables, 'tumblr:'))
        raise FandomError('record files are from an incompatable version of Fandometric (v {0}). Please import them into Fandometric {1}'.format(version, __version__))
    
    def _tables(self):
        yield '__info__', '\n'.join(k + '=' + v for k, v in (('__version__' , '.'.join(__version__)),
                                                             ('__time__'    , str(self.timestamp))))
        for url in chain(self._members, (self.gkey,)):
            yield 'tumblr:' + url, _users_serialize(self._UGS[url])
    
    def save(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
        S = '\n@'.join(table + ':::\n' + content for table, content in self._tables())
        with open(directory + '/' + str(max_file_index(directory) + 1) + '.txt', 'w') as fi:
            fi.write(S)
            fi.write('\n')
    
    ## comparison methods ##
    
    def since(self, other):
        osets = other.fsets
        fsets = self.fsets
        for url in self._members:
            if url in osets:
                A = osets[url]
                B = fsets[url]
                yield url, A - B, B - A
            else:
                yield url, None , None
    
    def stats(self):
        threshold = 604800
        denom     = len(self._UGS[self.gkey])
        for url in chain((self.gkey,), self._members):
            users = self._UGS[url]
            inactive_n = inactive(self.timestamp, users, threshold)
            try:
                ratio = round(len(users)/denom, 3)
            except ZeroDivisionError:
                ratio = 'undefined'
            yield (url,
                   ratio,
                   '{0} : {1}'.format(len(users), denom),
                   percent(inactive_n, len(users)),
                   inactive_n)

    def list_following(self):
        fsets = iter(self.fsets.values())
        f0    = next(fsets)
        follows_on_any = set.union(set(f0), * fsets)
        for i, (url, t) in enumerate(sorted(self._UGS[self.gkey], key=lambda k: k[1], reverse=True)):
            yield t, url in follows_on_any, url

def inactive(T, blogs, threshold):
    return sum(1 for blog in blogs if T - blog[1] > threshold)

def percent(a, b, roundto=3):
    try:
        p = str(round(a/b * 100, roundto)) + '%'
    except ZeroDivisionError:
        p = 'undefined'
    return p

def get_record(directory, N):
    with open(directory + '/' + str(N) + '.txt', 'r') as F:
        return User_group.from_file(F)
