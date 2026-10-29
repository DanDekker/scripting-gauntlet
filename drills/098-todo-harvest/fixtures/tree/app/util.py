#TODO: no space after the hash, so this is not a marker
# TODO(-): untangle the retry loop

def slug(value):
    # todo: lowercase is not the marker either
    return value.strip().lower().replace(" ", "-")
