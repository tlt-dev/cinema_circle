from datetime import datetime, timedelta

def get_time_delta(date):
    """ Get the time delta between today and the user interaction date"""
    delta = datetime.now() - date
    return delta.days

def calculate_like_weight():
    pass