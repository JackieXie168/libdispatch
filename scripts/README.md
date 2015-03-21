# Build Scripts and Data

## gen_version_scripts.py
This is a script to regenerate the following:
- libdispatch_globals.version: ld version script to hide unwanted symbols
  (from pthread_workqueue and kqueue) from libdispatch.so
- libdispatch_globals.regex: regular expression used by `static_link.py`.

## static_link.py
Script that merges static archives, and makes local any symbols with hidden
visibility as well as all those not matching a given regular expression.
