#!/usr/bin/env python3.5
import sys, traceback, webbrowser
from datetime import datetime

import src as fm

from flask import Flask, send_from_directory, render_template
from flask_socketio import SocketIO, emit

ui              = fm.ui

new_bubble      = ui.new_bubble
error_bubble    = ui.error_bubble
exception_bubble= ui.exception_bubble
FandomError     = ui.FandomError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=None)
streamer = ui.Streamer()
stream   = streamer.stream
ui.sleep = socketio.sleep

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    streamer.kill = True
    return render_template('index.html')


def _ARG_update(commands):
    if commands:
        new_bubble('output')
        fm.update_c(commands, stream)
    else:
        raise FandomError('no blog name given')

                                    # for windows
dateformat = '{0:%B} {0.day}, {0:%Y} at {1}:{0.minute:02} {0:%p}'.format
def int_to_date(t):
    T = datetime.fromtimestamp(t)
    return dateformat(T, (T.hour - 1) % 12 + 1)

state_key       = 'blog-deleted'    , 'blog-exists', 'blog-unknown', 'blog-new'
mutuality_key   = 'blog-nonmutual'  , 'blog-mutual',

def _to_table_row(info):
    return (None, state_key[info[0]]), (None, mutuality_key[info[1]]), ('<a href="https://{0}.tumblr.com">{0}</a>'.format(info[2]), 'blog-name')

def _emit_blog_rows(rows, css_class):
    emit('table', {'table': rows, 'head': len(rows), 'css_class': css_class, 'css_table_class': 'blogs-table', 'css_head_class': 'blogs-head'}, namespace='/py')

def _emit_element(tag, html, css_class=None):
    emit('element', {'tag': tag, 'html': html, 'css_class': css_class}, namespace='/py')

def _ARG_compare(commands):
    new_bubble('output')
    A, B, comparison = fm.compare_c(commands, stream)
    tA = int_to_date(A.timestamp)
    tB = int_to_date(B.timestamp)
    string = 'Movement on &lt;<span class="blog-name">{0}</span>&gt; from <span class="time">{1}</span> to <span class="time">{2}</span>'.format
    for table in comparison:
        if type(table) is tuple:
            _emit_element('div', string(table[0], tA, tB), 'movement-header')
            _emit_blog_rows(tuple(map(_to_table_row, table[1])), 'blogs-lost'  )
            _emit_blog_rows(tuple(map(_to_table_row, table[2])), 'blogs-gained')
        else:
            _emit_element('div', string(table, '—', tB), 'movement-header movement-header-error')

def _to_stats_row(info):
    info = iter(info)
    url  = next(info)
    if url[:2] != '__':
        return ('<span class="blog-name">{0}</span>'.format(url), * info )
    else:
        return (url, * info )
    
def _ARG_stats(commands):
    new_bubble('output')
    A, stats = fm.stats( * map(int, commands[:1]) , out=stream)
    string = 'Tumblr statistics for <span class="time">{0}</span>'.format(int_to_date(A.timestamp))
    _emit_element('div', string, 'stats-header')
    emit('table', {'table': tuple(map(_to_stats_row, stats)), 'thead': ('blog', 'ratio', 'n:m', 'inactive %', 'inactive n'), 'css_class': 'stats', 'css_table_class': 'stats-table'}, namespace='/py')

def _to_following_row(info):
    return (int_to_date(info[0]), 
            (None, mutuality_key[info[1]]), 
            ('<span class="blog-name"><a href="https://tumblr.com/unfollow/{0}">{0}</a></span>'.format(info[2]), None))

def _ARG_following(commands):
    new_bubble('output')
    A, following = fm.following( * map(int, commands[:1]) , out=stream)
    string = 'Blogs followed by primary &lt;<span class="blog-name">{0}</span>&gt; on <span class="time">{1}</span>'.format(A.primary, int_to_date(A.timestamp))
    _emit_element('div', string, 'following-header')
    emit('table', {'table': tuple(map(_to_following_row, following)), 'css_class': 'blogs-following', 'css_table_class': 'blogs-table'}, namespace='/py')

def _go(commands):
    try:
        with open('terminal.txt', 'r') as T:
            argstr = next(T).split()
    except FileNotFoundError:
        raise FandomError('No stored blog urls. Run `--cache` [`-c`] with `fm update` to store a set of urls.')
    _ARG_update(argstr)
    _ARG_compare([0, 1])
    _ARG_stats(())

_FM_COMMANDS = {'update'    : _ARG_update,
                'compare'   : _ARG_compare,
                'stats'     : _ARG_stats,
                'following' : _ARG_following,
                'go'        : _go}

_FM_CONFIRMED = {}

def _attempt_exec(func, arg):
    try:
        return func(arg)
    except FandomError as message:
        error_bubble(str(message))
    except:
        exception_bubble(traceback.format_exception( * sys.exc_info() ))

def _add_confirm(command, confirmed, prompt='', message='[{0}] continue?', fail='invalid input'):
    confirm_R = {'command': command, 'prompt': prompt}
    def confirm( * args ):
        new_bubble('output', message=message.format(command))
        emit('confirmation', confirm_R, namespace='/py')
    _FM_COMMANDS [command]  = confirm
    _FM_CONFIRMED[command]  = confirmed, fail, confirm_R

fm.authorize.build_key_receiver(app)
_add_confirm('tumblr-keys', fm.authorize.setup, 'passkey', message='Fandometric needs your tumblr keys in order to access your followers and following lists. You will only need to do this once. You can revoke its access at any time by going to Tumblr Settings > Apps on tumblr.com.', fail='Passkey invalid, try again...')

@socketio.on('connect', namespace='/py')
def test_for_client():
    client = fm.keys.make_client()
    if client is None:
        emit('need', 'fm tumblr-keys', namespace='/py')
    else:
        fm.keys.client = client

@socketio.on('fm confirm', namespace='/py')
def recieve_confirmation(response):
    key   = response['key']
    value = response['value']
    try:
        func, fail, confirm_R = _FM_CONFIRMED[key]
        new_bubble('command', confirm_R['prompt'] + '> ' + value)
        ui.sleep(0.005)
        O = _attempt_exec(func, value)
    except KeyError:
        print(key, 'NOT A VALID RESPONSE')
    else:
        if not O:
            new_bubble('error', message=fail)
            emit('confirmation', confirm_R, namespace='/py')
    emit('open', namespace='/py')

def parse_fm(commands):
    C, * commands = commands
    try:
        func = _FM_COMMANDS[C]
    except KeyError:
        raise FandomError("command '{0}' does not exist".format(C))
    else:
        func(commands)
    
@socketio.on('fm command', namespace='/py')
def on_command(command):
    streamer.kill = False
    new_bubble('command', command)
    ui.sleep(0.005)
    
    commands = command.split()
    if commands:
        program, * commands = commands
        if program == 'fm':
            if commands:
                # check that client is operational
                if fm.keys.client is None and commands[0] != 'tumblr-keys':
                    error_bubble('API keys were not generated properly. Regenerating keys...')
                    emit('need', 'fm tumblr-keys', namespace='/py')
                else:
                    _attempt_exec(parse_fm, commands)
        else:
            error_bubble("'{}' is not a recognized command".format(program))
    
    emit('open', namespace='/py')

@socketio.on('kill', namespace='/py')
def kill():
    print('Interrupted operation')
    streamer.kill = True

if __name__ == '__main__':
    webbrowser.open(url='http://localhost:1989')
    socketio.run(app, host='0.0.0.0', port=1989)
    
