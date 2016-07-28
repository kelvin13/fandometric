from flask_socketio import emit

from time import sleep

class FandomError(Exception):
    pass

class Colors:
    WARNING = 'warning'
    WORKING = 'working'

class _State_context(object):
    def __init__(self):
        self.bubble_count = -1
_STATE = _State_context()

def new_bubble(bubbletype, message=''):
    _STATE.bubble_count += 1
    emit('make bubble', {'type': bubbletype, 'i': _STATE.bubble_count, 'msg': message}, namespace='/py')
    return _STATE.bubble_count

class Streamer(object):
    def __init__(self):
        self.kill  = False
        self._state= _STATE
    
    def stream(self, content='', new=None):
        if self.kill:
            self.kill = False
            raise FandomError('operation killed')
        if new is not None:
            new_bubble(new)
        else:
            emit('stream', {'i': self._state.bubble_count, 'status': content}, namespace='/py')

def error_bubble(message):
    new_bubble('error', message)

def exception_bubble(exception_components):
    for error in exception_components:
        new_bubble('exception', error)
