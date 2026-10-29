"""Generate the corpus for 157-lua-needle-haystack.

The binary file carries a NUL byte and the needle, and two files use CRLF, so none of
them can be committed as clean text.
"""

import os
from pathlib import Path

inp = Path(os.environ["IN"])
corpus = inp / "corpus"
(corpus / "sub").mkdir(parents=True, exist_ok=True)

FILES = {
    "alpha.log": b"intro\nneedle token=100% here\noutro\n",
    "crlf.log": b"first\r\ntoken=100% tail\r\n",
    "epsilon.log": b"nothing to see here\n",
    "sub/beta.txt": b"token=100%\n",
    "sub/gamma.log": b"a\na token=100% b token=100% c\n",
    "delta.bin": b"\x00\x00token=100%\n",
}

for name, blob in FILES.items():
    (corpus / name).write_bytes(blob)
