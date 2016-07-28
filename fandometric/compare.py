from .arc import get_record, max_file_index
from .fetch import exists

from . import ui

def check(A, B):    
    mutuals = B.gset
    def survey_lost(url):
        return exists(url), url in mutuals, url
    
    def survey_gained(url):
        return 3          , url in mutuals, url
    
    # 0-Deleted, 1-Exists, 2-Unknown, 3-New
    for url, lost, gained in B.since(A):
        if lost is None:
            yield url
        else:
            yield url, map(survey_lost, lost), map(survey_gained, gained)

def compare(a=0, b=None, directory='records', out=print):
    if b is None:
        b = a
    
    n = max_file_index(directory)
    a, b = sorted((n - abs(a), n - abs(b)))
    
    out('Checking blog movement between records {0} and {1}...'.format(a, b))
    ui.sleep(0.001)
    try:
        A = get_record(directory, a)
        B = get_record(directory, b)
    except FileNotFoundError as message:
        if n <= 1:
            raise ui.FandomError(' Comparisons require more than one snapshot. Please try running fandometric.update again later.')
        else:
            raise
    else:
        return A, B, check(A, B)

def compare_c(commands, out):
    return compare( * map(int, commands[:2]) , out=out)
