import random, string

def generate_random_string(length):
    random_string = ''
    for i in range(0,length):
        random_string = random_string + random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
    return random_string