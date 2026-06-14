"""Allow running the package directly: python -m speechlens <file>"""

import sys

from .cli import main

sys.exit(main())
