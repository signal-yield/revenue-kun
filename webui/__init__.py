"""Local Step 3 Web UI for revenue-kun.

This package is a thin adapter outside `src/revenue_kun/`. It must import
and call the existing CLI domain functions directly; it must not call
`revenue_kun.cli.run()`, invoke `src/main.py` via subprocess, or duplicate
extraction / NOI / Excel-generation logic. See Issue #78 for the approved
architecture decision and Issue #79 for this foundation's scope.
"""
