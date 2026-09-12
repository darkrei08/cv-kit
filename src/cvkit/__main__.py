# -*- coding: utf-8 -*-
"""Allow ``python -m cvkit ...`` as an alternative to the console script.

Both entry points must work: the ``cvkit`` command is created by the package
installer, while ``python -m cvkit`` works from a source checkout without putting
anything on PATH. Documentation that mentions one and not the other is confusing, and
a CI step that calls ``python -m cvkit doctor`` fails with a message about a missing
module rather than about the tool.
"""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
