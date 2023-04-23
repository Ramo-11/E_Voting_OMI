import random
import math

import Crypto.Util.number as number

class Paillier:
    pubkey = None
    privkey = None
    def __init__(self, key_length):
        p = number.getPrime(key_length // 2)
        q = number.getPrime(key_length // 2)       
        #p = 46183
        #q = 48907
        self.pubkey, self.privkey = self.generate_keypair(p , q)

    def generate_keypair(self,p, q):
        n = p * q
        lam = (p - 1) * (q - 1)
        mu = number.inverse(lam , n)
        return n, (lam , mu)
    
    def get_pubkey(self):
        return self.pubkey
    
    def get_keylength(self):
        return 2048

    def encrypt(self,m, pubkey):
        n = pubkey
        r = self.random_coprime(n)
        #r = 37404609
        #g = n + 1    
        c1 = pow(1 + n, m, n**2)
        c2 = pow(r, n, n**2)
        c = (c1 * c2) % (n**2)
        return c

    def random_coprime(self,n):
        while True:
            r = random.randint(1, n-1)
            if math.gcd(r, n) == 1:
                return r

    def decrypt(self,c, privkey, n):
        lam, mu = privkey
        if not 0 < c < n**2:
            raise ValueError('ciphertext out of range')
        
        # Check if c is coprime with n
        if math.gcd(c, n) != 1:
            raise ValueError('ciphertext not coprime with modulus')
        
        # Compute L function
        plaintext = (pow(c, lam, n**2) - 1) // n * mu % n
        
        return plaintext


def initialize_paillier():
    return Paillier(key_length=2048)


# To test:

# Instantiate the Paillier cryptosystem with a key length of 1024 bits
# p = Paillier(key_length=2048)

# n = p.get_pubkey()
# print(f'\npublic key is: {n}')
# print(f'\nprivate key is: {p.privkey}')

# message = b = b'hello,34'
# message = int.from_bytes(b, byteorder='big')

# print(f'\nmessage is: {message}')

# # Encrypt the plaintext message "123456"
# ciphertext = p.encrypt(message,n)

# # Decrypt the ciphertext
# decrypted_message = p.decrypt(ciphertext , p.privkey,p.pubkey)

# # Print the results
# print("\nCiphertext:", ciphertext)

# message = decrypted_message.to_bytes((decrypted_message.bit_length() + 7) // 8, byteorder='big')

# print("\nDecrypted message:", message)

