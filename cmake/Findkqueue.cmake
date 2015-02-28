include (FindPackageHandleStandardArgs)
include (CheckFunctionExists)

find_package(Threads)

find_path(KQUEUE_INCLUDE_DIR sys/event.h PATH_SUFFIXES kqueue)
set(KQUEUE_INCLUDE_DIRS "${KQUEUE_INCLUDE_DIR}")

check_function_exists(KQUEUE_IN_LIBC kqueue)
find_library(KQUEUE_LIBRARY kqueue)

set(required_vars KQUEUE_INCLUDE_DIR)
set(KQUEUE_LIBRARIES "")

if (NOT KQUEUE_RUNTIME_IN_LIBC)
  list(APPEND required_vars KQUEUE_LIBRARY)
  if (KQUEUE_LIBRARY)
    list(APPEND KQUEUE_LIBRARIES "${KQUEUE_LIBRARY};${CMAKE_THREAD_LIBS_INIT}")
  endif ()
endif ()

find_package_handle_standard_args(kqueue
  REQUIRED_VARS ${required_vars}
)
