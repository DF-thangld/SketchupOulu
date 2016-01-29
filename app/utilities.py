import random, string


def generate_random_string(length):
    random_string = random.choice(string.ascii_lowercase + string.ascii_uppercase)
    for i in range(1,length):
        random_string = random_string + random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
    return random_string


def format_datetime(datetime):
    if datetime is not None:
        return datetime.isoformat()
        #return datetime.strftime("%d.%m.%Y %h:%M:%S")
    return None
