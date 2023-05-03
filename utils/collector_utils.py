import random
import time

def generate_random_shares():
        random.seed(time.time_ns() // 1_000_000)

        num_list = list(range(20, 1500))

        random_nums = random.sample(num_list, 2)

        x = int(random_nums[0])
        x_prime = int(random_nums[1])

        return [x, x_prime]