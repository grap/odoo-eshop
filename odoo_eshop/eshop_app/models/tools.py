def currency(value):
    if not value:
        value = 0
    return ("%.02f" % value).replace(".", ",") + " €"
