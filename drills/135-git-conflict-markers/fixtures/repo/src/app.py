import os


def main():
    print("hello")


<<<<<<< HEAD
def legacy_path():
    return os.path.join("a", "b")
=======
def new_path():
    return os.path.join("c", "d")
>>>>>>> feature/paths


def other():
<<<<<<< HEAD
    return 1
||||||| base
    return 0
=======
    return 2
>>>>>>> fix/return
