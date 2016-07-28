from . import nest

from .compare import compare_c
from .update import update_c
from .arc import get_record, max_file_index

from . import ui

def _record_method(message, methodname):
    def f(a=0, directory='records', out=print):
        n = max_file_index(directory)
        a = n - abs(a)
        
        out(message.format(a))
        ui.sleep(0.001)
        
        A = get_record(directory, a)
        return A, getattr(A, methodname)()
    return f

stats       = _record_method('Calculating statistics on record {0}...', 'stats'         )
following   = _record_method('Listing followers on record {0}...'     , 'list_following')
