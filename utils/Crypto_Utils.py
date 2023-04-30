import random
import math
# from sympy import isprime

def get_prime(n):
    """
    Generate a random N-bit prime number.
    """
    while True:
        # Generate a random odd integer with N bits
        p = random.getrandbits(n) | (1 << n-1) | 1
        # Check if p is prime
        if is_prime(p):
            return p

def inverse(u, v):
    """
    Calculate the inverse of u mod v.
    """
    # Initialize variables
    u1, u2, u3 = 1, 0, u
    v1, v2, v3 = 0, 1, v
    
    # Apply the extended Euclidean algorithm
    while v3 != 0:
        q = u3 // v3
        t1, t2, t3 = u1 - q*v1, u2 - q*v2, u3 - q*v3
        u1, u2, u3 = v1, v2, v3
        v1, v2, v3 = t1, t2, t3
        
    # Check if the gcd is 1 (i.e., if u and v are coprime)
    if u3 != 1:
        raise ValueError("u and v are not coprime")
    
    # Return the inverse
    return u1 % v

def is_prime(n):
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    # if n in generate_primes_in_range(10**8):
    #     return True
    # if is_strong_probable_prime(n):
    #     return True
    return miller_rabin_prime_test(n)
    
def generate_primes_in_range(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    primes = [i for i in range(limit + 1) if is_prime[i]]
    return primes

def is_strong_probable_prime(n):
    if n == 2:
        return True
    if n < 2 or n % 2 == 0:
        return False

    # Compute D and S such that n-1 = 2^S * D
    S, D = 0, n - 1
    while D % 2 == 0:
        S += 1
        D //= 2

    # Choose P and Q such that D = P^2 - 4*Q
    P, Q = 1, (1 - D) // 4
    while not is_square(P - 2*Q):
        P += 2
        Q += P - D
    U, V = (P, 1), ((P*P - 2*Q) // n, (2*P) % n)

    # Perform the Lucas sequence until the nth term
    for i in range(S - 1, -1, -1):
        U, V = ((U[0]*V[0] + U[1]*V[1]) % n, (P*U[0] + V[0]*U[1]*D) % n), ((V[0]*V[0] + V[1]*V[1]) % n, (2*V[0]*V[1]) % n)
        if i == 0 or i == S - 1:
            continue
        if U[1] == 0:
            return True
    return U[0] == 0

def is_square(n):
    if n < 0:
        return False
    if n == 0:
        return True
    lo, hi = 0, n
    while lo <= hi:
        mid = (lo + hi) // 2
        sq = mid * mid
        if sq == n:
            return True
        elif sq < n:
            lo = mid + 1
        else:
            hi = mid - 1
    return False

def miller_rabin_prime_test(n, rounds=5):
    if n == 2 or n == 3:
        return True
    if n < 2 or n % 2 == 0:
        return False
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True
