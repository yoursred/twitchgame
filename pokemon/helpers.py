import random

def random_set(a, b, s):
    return [random.randint(a, b) for _ in range(s)]


def normalize_name(name):
    return name\
        .replace(" ", "")\
        .replace("-", "")\
        .replace(".", "")\
        .replace("\'", "")\
        .replace("%", "")\
        .replace("*", "")\
        .replace(":", "")\
        .strip()\
        .lower()\
        .encode('ascii', 'ignore')\
        .decode('utf-8')
