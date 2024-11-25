import random
import datetime

def random_date_of_bith():
    starting_date = datetime.date(1990,1,1)
    ending_date = datetime.date(2005,12,31)

    date_range = (ending_date - starting_date).days
    random_days = random.randint(0, date_range)

    random_date = starting_date + datetime.timedelta(days = random_days)
    
    return random_date

def random_education_level():
    levels = ['PRIMARY', 'SECONDARY', 'ASSOCIATE', 'BACHELOR', 'MASTER', 'DOCTORATE']
    random_level = random.randint(0,len(levels)-1)
    return levels[random_level]

def id_generator(n: int):
    i = 0
    while i < n:
        yield i
        i = i + 1

def random_years_of_experience():
    return random.randint(0,10)

def random_first_time():
    return bool(random.randint(0,1))

def random_capacity(low = 20000, high = 100000):
    return random.randint(low, high)
