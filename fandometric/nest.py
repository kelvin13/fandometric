from .output import succ, fail, bold, endc
import importlib

# test to make sure modules are installed

def test( * modules ):
    for module in modules:
        try:
            importlib.import_module(module)
        
        except ImportError:
            yield module

missing = tuple(test('httplib2', 'flask'))
if missing:
    print(fail, 'Warning, you are missing the following required packages:', endc, sep='')
    for module in missing:
        print(fail, bold, module, endc)
    while True:
        install = input(succ + 'Install packages? [y/n] > ' + endc).lower()
        if install == 'y':
            import pip
            try:
                for module in missing:
                    pip.main(['install', '--user', module])
            except:
                print(fail, 'Unable to install packages using pip3. Please try manual installation.', endc, sep='')
                quit()
            else:
                print(succ, bold, 'Dependencies successfully installed', endc , sep='')
                break
        elif install == 'n':
            quit()
