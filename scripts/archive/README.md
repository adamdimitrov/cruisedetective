# Archived one-off scripts. Do not run.

These scripts each made a one-time change to the site (a migration, a patch, an
optimisation pass, an old deck builder). They are kept for reference only.

Running one again can write an old state back over the current pages (for
example the old river-cruise deck builders would overwrite the current river
cruise page). Their paths also assume they live one folder higher, so they would
read and write the wrong files.

If you need what one of them did, write a new script that works from the
current pages, and check it with `python3 kit/checks/check_all.py`.
