__author__ = 'jjh'

def get_query_param(qs, name, default):
    return qs.get(name,[default])[0]