# libdispatch for Linux - Changelog

## 0.1.3.1 / 2015-10-06
- [BUGFIX] Speculative fix for a bug in Glibc's implementation of POSIX
  semaphores that could crash libdispatch.
- This is identical to 0.1.3, but with the correct version number.

## 0.1.2 / 2015-09-23
- [BUGFIX] Fix compiling public headers with GCC in C++ mode. (Issue #17)
- [BUGFIX] dispatch_main() no longer calls pthread_exit() internally, as
  calling pthread_exit() on the main thread appears to cause issues on
  Linux. E.g. some parts of /proc/PID become unuseable, (see:
  http://man7.org/linux/man-pages/man5/proc.5.html) and address sanitizer
  treats it as a fatal error.

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
