cmake_minimum_required(VERSION 2.8.7)

project (dispatch)
set (DISPATCH_VERSION 0.1.3.1)
set (DISPATCH_ABI_VERSION 1)

list (APPEND CMAKE_MODULE_PATH "${dispatch_SOURCE_DIR}/cmake")
include (BuildUtil)

include (CheckCCompilerFlag)
include (CheckCSourceCompiles)
include (CheckTypeSize)
include (CMakePushCheckState)

if (NOT CMAKE_BUILD_TYPE)
    set (CMAKE_BUILD_TYPE Release)
endif ()

option (DISPATCH_ENABLE_TEST_SUITE
    "Whether to build the test suite" NO)

option (DISPATCH_ENABLE_BLOCKS
    "Enable use of block-based API" YES)
option (DISPATCH_ENABLE_PTHREAD_WORKQUEUE
    "Enable use of the more efficient pthread workqueue library for thread pool support"
    YES)
option (DISPATCH_USE_LIBDISPATCH_INIT_CONSTRUCTOR
    "Use libdispatch_init as a constructor" YES)

if (NOT DISPATCH_ENABLE_PTHREAD_WORKQUEUE)
    set (CMAKE_DISABLE_FIND_PACKAGE_pthread_workqueue 1)
endif ()

if (NOT DISPATCH_ENABLE_BLOCKS)
    set (CMAKE_DISABLE_FIND_PACKAGE_BlocksRuntime 1)
endif ()

#///////////////////////////////////////////////////////////////////////////////
# Defines and compile flags
set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=gnu99")
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=gnu++98")
add_definitions(-D_GNU_SOURCE)

if (DISPATCH_SANITIZE)
    add_definitions( -g -fno-omit-frame-pointer )
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=${DISPATCH_SANITIZE}")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=${DISPATCH_SANITIZE}")
else ()
    set (CMAKE_SHARED_LINKER_FLAGS
         "${CMAKE_SHARED_LINKER_FLAGS} -Wl,--no-undefined")
endif ()

if (CMAKE_BUILD_TYPE MATCHES Debug)
    add_definitions(-DDISPATCH_DEBUG=1)
endif ()

if (CMAKE_C_COMPILER_ID MATCHES Clang)
    add_definitions( -fcolor-diagnostics )
endif ()

#///////////////////////////////////////////////////////////////////////////////
# Libraries and compiler features
find_package(kqueue REQUIRED)
find_package(pthread_workqueue)
find_package(BlocksRuntime)

check_c_compiler_flag(-fblocks COMPILER_HAS_BLOCKS_SUPPORT)

if (PTHREAD_WORKQUEUE_FOUND)
    dispatch_search_libs(pthread_workqueue_setdispatch_np LIBRARIES
        "${PTHREAD_WORKQUEUE_LIBRARIES}")

elseif (DISPATCH_ENABLE_PTHREAD_WORKQUEUE)
    set(DISPATCH_ENABLE_PTHREAD_WORKQUEUE FALSE)
    message(WARNING "Pthread Workqueues were not found; libdispatch will fall "
                    "back to a less sophisticated (and slower) thread pool "
                    "implementation.")
endif ()

if (DISPATCH_ENABLE_BLOCKS AND NOT COMPILER_HAS_BLOCKS_SUPPORT)
    set(DISPATCH_ENABLE_BLOCKS FALSE)
    message(WARNING "Blocks compiler support was not found; support for "
                    "blocks-based API (including dispatch I/O) will be "
                    "disabled.")
elseif (DISPATCH_ENABLE_BLOCKS AND NOT BLOCKSRUNTIME_FOUND)
    set(DISPATCH_ENABLE_BLOCKS FALSE)
    message(WARNING "A blocks runtime was not found; support for blocks-based "
                    "API (including dispatch I/O) will be disabled.")
endif ()

if (DISPATCH_ENABLE_BLOCKS)
    add_definitions(-fblocks)
elseif (COMPILER_HAS_BLOCKS_SUPPORT AND NOT DISPATCH_ENABLE_BLOCKS)
    add_definitions(-fno-blocks)
endif ()

add_subdirectory(config)

#///////////////////////////////////////////////////////////////////////////////

include_directories(SYSTEM fixincludes)

add_subdirectory(src)

if (NOT DISPATCH_ENABLE_TEST_SUITE)
    message(STATUS "Skipping test suite")
elseif (NOT DISPATCH_ENABLE_BLOCKS)
    message(WARNING "Cannot build test suite -- we need both a Blocks Runtime "
                    "and compiler support for Blocks.")
else ()
    add_subdirectory(testing)
endif ()

# Install man pages
add_subdirectory(man)

# Install public headers
add_subdirectory(dispatch)
add_subdirectory(os)
