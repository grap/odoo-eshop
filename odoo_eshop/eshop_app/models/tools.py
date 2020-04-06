# encoding: utf-8

def currency(n):
    if not n:
        n = 0
    return ('%.02f' % n).replace('.', ',') + u' €'
