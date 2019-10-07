import random
import string


def random_str(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

