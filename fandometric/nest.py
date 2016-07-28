import importlib

# test to make sure modules are installed

def test( * modules ):
    for module in modules:
        try:
            importlib.import_module(module)
        
        except ImportError:
            yield module

missing = tuple(test('httplib2', 'flask', 'flask_socketio', 'eventlet'))
if missing:
    print('Warning, you are missing the following required packages:')
    for module in missing:
        print(module)
    while True:
        install = input('Install packages? [y/n] > ').lower()
        if install == 'y':
            import pip
            try:
                for module in missing:
                    pip.main(['install', '--user', module])
            except:
                print('Unable to install packages using pip3. Please try manual installation.')
                quit()
            else:
                print('Dependencies successfully installed')
                break
        elif install == 'n':
            quit()
