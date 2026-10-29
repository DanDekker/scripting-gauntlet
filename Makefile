PY ?= python3
H  := $(PY) harness/run.py

.PHONY: help list check new lint

help:
	@echo "make list              list drills"
	@echo "make check             run every drill x every solution"
	@echo "make new ID=007-slug   scaffold a drill"
	@echo "make lint              compile-check python sources"

list:
	@$(H) list

check:
	@$(H) run all

new:
	@test -n "$(ID)" || (echo "ID=... required" && exit 1)
	@$(H) new $(ID)

lint:
	@$(PY) -m compileall -q harness drills && echo "python: ok"
	@for f in $$(find drills -name 'solve.bash' -o -name 'solve.sh'); do bash -n "$$f" || exit 1; done; echo "bash: ok"
	@for f in $$(find drills -name 'solve.zsh'); do zsh -n "$$f" || exit 1; done; echo "zsh: ok"
	@for f in $$(find drills -name 'solve.lua'); do luac -p "$$f" || exit 1; done; echo "lua: ok"
	@$(PY) harness/check_skills.py
