"""Create the intentionally BOM-less UTF-16LE fixture in the harness work tree."""

import os
from pathlib import Path


content = "INFO|job started\nWARN| café cache low \n\nERROR|disk full\nINFO|job done\n"
Path(os.environ["IN"], "events.log").write_bytes(content.encode("utf-16-le"))
