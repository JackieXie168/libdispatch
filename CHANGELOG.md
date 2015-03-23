# libdispatch for Linux - Changelog

## 0.2.0 / Unreleased
- libdispatch is now self-contained, no longer relying on system version of
  libpthread_workqueue and libkqueue. libdispatch builds and links to private
  versions of these libraries that are not exported from the static or shared
  library variants.
- libBlocksRuntime is also bundled, however unlike the aforementioned libraries
  its symbols *are* exported. blocksRuntime's symbols can be overridden by
  those provided by another blocks implementation provided its .so appears
  before libdispatch in your link line.
- Merge Mavericks changes.

## 0.1.1 / 2015-03-12
- [BUGFIX] Fix leaking of internal symbols from libdispatch.so

## 0.1.0 / 2015-02-22
- Initial release.
- [BUGFIX] dispatch io: improved handling of buffer allocation failures.
- Remove unmaintained autotools build system; use CMake exclusively. A
  configure script is provided to invoke CMake with the right options.
- Change signatures of the nonportable (`_np` suffixed) io/data functions to
  match what Apple's ones use in the Mavericks release of libdispatch.
- Rename `dispatch_get_main_queue_eventfd_np()` to
  `dispatch_get_main_queue_handle_np()`.
- Bump ABI version to 1 as a result of these signature changes.
