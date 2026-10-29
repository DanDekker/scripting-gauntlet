import os


def load(path):
    # TODO(alice): validate the path before opening
    print("TODO: this string is not a marker")
    return open(path).read()


def main():
    print(load(os.environ["CONFIG"]))
