include (FindPackageHandleStandardArgs)
include (CheckFunctionExists)

find_path(BLOCKSRUNTIME_PUBLIC_INCLUDE_DIR Block.h
  DOC "Path to Block.h"
)

if (BLOCKSRUNTIME_PUBLIC_INCLUDE_DIR)
  list (APPEND BLOCKSRUNTIME_INCLUDE_DIRS "${BLOCKSRUNTIME_PUBLIC_INCLUDE_DIR}")
endif ()

find_path(BLOCKSRUNTIME_PRIVATE_INCLUDE_DIR Block_private.h
  DOC "Path to Block_private.h"
)
if (BLOCKSRUNTIME_PRIVATE_INCLUDE_DIR)
  list (APPEND BLOCKSRUNTIME_INCLUDE_DIRS "${BLOCKSRUNTIME_PRIVATE_INCLUDE_DIR}")
  set (BLOCKSRUNTIME_PRIVATE_HEADERS_FOUND TRUE)
endif ()

set(required_vars
    BLOCKSRUNTIME_PUBLIC_INCLUDE_DIR
    BLOCKSRUNTIME_PRIVATE_INCLUDE_DIR)
set(BLOCKSRUNTIME_LIBRARIES "")

check_function_exists(BLOCKSRUNTIME_RUNTIME_IN_LIBC _Block_copy)
find_library(BLOCKSRUNTIME_LIBRARY "BlocksRuntime" DOC "Path to the blocks runtime library")

if (NOT BLOCKSRUNTIME_RUNTIME_IN_LIBC)
  list(APPEND required_vars BLOCKSRUNTIME_LIBRARY)
  if (BLOCKSRUNTIME_LIBRARY)
    list(APPEND BLOCKSRUNTIME_LIBRARIES "${BLOCKSRUNTIME_LIBRARY}")
  endif ()
endif ()

find_package_handle_standard_args(BlocksRuntime
  REQUIRED_VARS ${required_vars})

