`setup.py` generates `in/tree/` with fixed byte sizes.

Nothing here is committed as a real file: the drill needs hardlinks, a symlink loop and
several megabytes of data, none of which belong in git.
