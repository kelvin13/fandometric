"""
import pytumblr
import pickle
import time
import datetime

greatArchive = pickle.load(open("archive.txt", 'rb'))

for i, (time, R) in enumerate(sorted(greatArchive.items(), key=lambda t: t[0])):
    with open('records/' + str(i) + '.txt', 'w') as fi:
        fi.write(str(time) + '\n')
        print(i, [r for r in R if r is None])
        fi.write('\n'.join(r + '|-1' for r in R if r is not None))
        fi.write('\n~~~\n')

"""
import os

def max_file_index(directory):
    return max(int(os.path.splitext(name)[0]) for name in next(os.walk(directory))[2])

def write_record(time, urls1, urls2, directory='records'):
    S = str(time) + '\n' + '\n'.join(urls1) + '\n~~~\n' + '\n'.join(urls2) + '\n'
    with open(directory + '/' + str(max_file_index(directory) + 1) + '.txt', 'w') as fi:
        fi.write(S)

#write_record(-1, ['taylorswift', 'abiander'], ['taylorswift'])
