import hashlib

def generate_key(password):
    return hashlib.sha224(password.encode()).hexdigest()

def encode(password, string):
    key = generate_key(password)
    return [ord(string[i]) + ord(key[i % len(key)]) for i in range(len(string))]

def decode(password, L):
    key = generate_key(password)
    return ''.join(map(chr, (L[i] - ord(key[i % len(key)]) for i in range(len(L)))))

if __name__ == '__main__':
    import sys
    print(encode(sys.argv[2], sys.argv[1]))
