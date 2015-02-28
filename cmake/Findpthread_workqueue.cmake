include (FindPackageHandleStandardArgs)
include (CheckFunctionExists)

find_path(PTHREAD_WORKQUEUE_INCLUDE_DIR pthread_workqueue.h)
set(PTHREAD_WORKQUEUE_INCLUDE_DIRS "${PTHREAD_WORKQUEUE_INCLUDE_DIR}")

check_function_exists(PTHREAD_WORKQUEUE_IN_LIBC pthread_workqueue_create_np)
find_library(PTHREAD_WORKQUEUE_LIBRARY pthread_workqueue)

set(required_vars PTHREAD_WORKQUEUE_INCLUDE_DIR)
set(PTHREAD_WORKQUEUE_LIBRARIES "")

if (NOT PTHREAD_WORKQUEUE_IN_LIBC)
  list(APPEND required_vars PTHREAD_WORKQUEUE_LIBRARY)
  if (PTHREAD_WORKQUEUE_LIBRARY)
    list(APPEND PTHREAD_WORKQUEUE_LIBRARIES "${PTHREAD_WORKQUEUE_LIBRARY}")
  endif ()
endif ()


find_package_handle_standard_args(pthread_workqueue
  REQUIRED_VARS ${required_vars}
)
