import random
import math

from Crypto.Util import number

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

    @staticmethod
    def encrypt(m, pubkey):
        n = pubkey
        r = Paillier.random_coprime(n)
        #r = 37404609
        #g = n + 1    
        c1 = pow(1 + n, m, n**2)
        c2 = pow(r, n, n**2)
        c = (c1 * c2) % (n**2)
        return c

    @staticmethod
    def random_coprime(n):
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