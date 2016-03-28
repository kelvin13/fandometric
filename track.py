from tumblr_keys import client
from jamestaylor import max_file_index

_fail = '\033[91m'
_bold = '\033[1m'
_endc = '\033[0m'
_succ = '\033[92m'

def itemize(N):
    with open('records/' + str(N) + '.txt', 'r') as F:
        followers, following = F.read().split('~~~')
        T, * followers = followers.split()
        followers = [blog.split('|') for blog in followers]
        following = [blog.split('|') for blog in following.split()]
        return T, followers, following

def exists(blog):
    if "meta" in client.blog_info(blog) and "status" in client.blog_info(blog)["meta"]:
        if client.blog_info(blog)["meta"]["status"] == 404:
            return False
        else:
            print (blog + " [other error?]")
            return False
    else:
        return True

def inactive(T, blogs, roundto=5):
    count = sum(T - float(U[1]) > 604800 for U in blogs)
    return count, round(count/len(blogs) * 100, roundto)
def stats(T, followers, following):
    print('\n' + _bold + 'ratio = ' + str(round(len(followers)/len(following), 5)) + _endc)
    inactive_following = inactive(T, following)
    print(str(inactive_following[1]) + '% inactive following (' + str(inactive_following[0]) + ' blogs)')
    inactive_followers = inactive(T, followers)
    print(str(inactive_followers[1]) + '% inactive followers (' + str(inactive_followers[0]) + ' blogs)')
    
def check(N):
    T1, followers1, following1 = itemize(N - 1)
    T2, followers2, following2 = itemize(N)
    
    following_url_set2 = set(U[0] for U in following2)
    follower_url_set2 = set(U[0] for U in followers2)
    M = {True: _fail + _bold + 'mutual' + _endc, False: '—'}
    for U in followers1:
        if U[0] not in follower_url_set2:
            exmutual = M[U[0] in following_url_set2]
            if exists(U[0]):
                print(' \t'.join(('exists ', exmutual, U[0], 'http://' + U[0] + '.tumblr.com')))
            else:
                print(' \t'.join((_fail + 'deleted' + _endc, exmutual, U[0], 'http://' + U[0] + '.tumblr.com')))

    follower_url_set1 = set(U[0] for U in followers1)
    M = {True: _succ + 'mutual' + _endc, False: '—'}
    for U in followers2:
        if U[0] not in follower_url_set1:
            exmutual = M[U[0] in following_url_set2]
            print(' \t'.join(('\033[92m' + 'new    ' + _endc, exmutual, U[0], 'http://' + U[0] + '.tumblr.com')))

    stats(float(T2), followers2, following2)

check(max_file_index('records'))


        
"""
referenceList = greatArchive[sorted(greatArchive.keys())[-2]]
newList = greatArchive[sorted(greatArchive.keys())[-1]]

unfollowers = [x for x in list(set(referenceList) - set(newList)) if x is not None]
newfollowers = [x for x in list(set(newList) - set(referenceList)) if x is not None]

print (str(len(unfollowers)) + " unfollowers:")

for i in unfollowers:
    if "meta" in client.blog_info(i) and "status" in client.blog_info(i)["meta"]:
        if client.blog_info(i)["meta"]["status"] == 404:
            print (i + " [deleted]")
        else:
            print (i + " [other error?]")
    else:
        if i in followingDict.values():
            print ('http://' + i + '.tumblr.com' + ' exmutual')
        else:
            print ('http://' + i + '.tumblr.com')

print (str(len(newfollowers)) + " new followers:")
for i in newfollowers:
        print (i)

print ("ratio: " + str(count/client.info()["user"]["following"]))
"""
