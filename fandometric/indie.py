import os

def max_file_index(directory):
    return max(int(os.path.splitext(name)[0]) for name in next(os.walk(directory))[2])

def write_record(time, urls1, urls2, directory):
    S = ''.join((str(time), '\n', '\n'.join(urls1), '\n~~~\n', '\n'.join(urls2), '\n'))
    with open(directory + '/' + str(max_file_index(directory) + 1) + '.txt', 'w') as fi:
        fi.write(S)

#write_record(-1, ['taylorswift', 'abiander'], ['taylorswift'])
