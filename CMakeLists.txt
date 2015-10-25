cmake_minimum_required(VERSION 2.8.7)

project (dispatch)
set (DISPATCH_VERSION 0.1.3.1)
set (DISPATCH_ABI_VERSION 1)

list (APPEND CMAKE_MODULE_PATH "${dispatch_SOURCE_DIR}/cmake")
include (BuildUtil)

include (CheckCCompilerFlag)
include (CheckCSourceCompiles)
include (CheckTypeSize)
include (CMakeDependentOption)
include (CMakePushCheckState)
include (GNUInstallDirs)

if (NOT CMAKE_BUILD_TYPE)
    set (CMAKE_BUILD_TYPE Release)
endif ()

option (DISPATCH_ENABLE_TEST_SUITE
    "Whether to build the test suite" FALSE)

option (DISPATCH_ENABLE_BLOCKS
    "Enable use of block-based API" TRUE)
option (DISPATCH_ENABLE_PTHREAD_WORKQUEUE
    "Enable use of the more efficient pthread workqueue library for thread pool support"
    TRUE)
cmake_dependent_option(
    DISPATCH_USE_PRIVATE_BLOCKSRUNTIME
    "Whether to use libdispatch's private blocks runtime"
    TRUE
    DISPATCH_ENABLE_BLOCKS
    FALSE)
cmake_dependent_option(
    DISPATCH_USE_PRIVATE_PTHREAD_WORKQUEUE
    "Whether to use libdispatch's private pthread workqueues implementation"
    TRUE
    DISPATCH_ENABLE_PTHREAD_WORKQUEUE
    FALSE)
option (DISPATCH_USE_PRIVATE_KQUEUE
    "Whether to use libdispatch's private kqueue implementation"
    TRUE)

option (DISPATCH_USE_LIBDISPATCH_INIT_CONSTRUCTOR
    "Use libdispatch_init as a constructor" TRUE)

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
check_c_compiler_flag(-fblocks COMPILER_SUPPORTS_BLOCKS)

if (DISPATCH_USE_PRIVATE_KQUEUE)
    dispatch_add_subproject(kqueue
        SOURCE_DIR thirdparty/libkqueue
        INSTALL_PREFIX thirdparty/kqueue-subproject
        LIBRARY lib/libkqueue.a
        INCLUDE_DIR include/kqueue)

else ()
    find_package(kqueue REQUIRED)
    cmake_push_check_state()
        set( CMAKE_REQUIRED_INCLUDES "${KQUEUE_INCLUDE_DIRS}" )
        set( CMAKE_REQUIRED_LIBRARIES "${KQUEUE_LIBRARIES}" )
        # FIXME: When using bundled kqueue, we should set these feature
        # detection macros.
        dispatch_check_decls(
            EV_SET64 NOTE_NONE NOTE_REAP NOTE_REVOKE NOTE_SIGNAL
            NOTE_LEEWAY NOTE_NSECONDS NOTE_ABSOLUTE
            INCLUDES sys/event.h
        )
        check_type_size("struct kevent64_s" DECL_KEVENT64_S)
        dispatch_check_funcs( kevent64 )
    cmake_pop_check_state()
endif()

if (DISPATCH_USE_PRIVATE_PTHREAD_WORKQUEUE)
    dispatch_add_subproject(pthread_workqueue
        SOURCE_DIR thirdparty/libpthread_workqueue
        INSTALL_PREFIX thirdparty/pthread_workqueue-subproject
        LIBRARY lib/libpthread_workqueue.a
        LIBRARY_DEBUG lib/libpthread_workqueueD.a)

elseif (DISPATCH_ENABLE_PTHREAD_WORKQUEUE)
    find_package(pthread_workqueue)

    if (PTHREAD_WORKQUEUE_FOUND)
        dispatch_search_libs(pthread_workqueue_setdispatch_np LIBRARIES
            "${PTHREAD_WORKQUEUE_LIBRARIES}")
    else ()
        set(DISPATCH_ENABLE_PTHREAD_WORKQUEUE FALSE)
        message(WARNING "Pthread Workqueues were not found; libdispatch will "
                        "fall back to its naive thread pool implementation.")
    endif ()
endif ()

if (DISPATCH_ENABLE_BLOCKS AND NOT COMPILER_SUPPORTS_BLOCKS)
    set(DISPATCH_ENABLE_BLOCKS FALSE)
    message(WARNING "Blocks compiler support was not found; support for "
                    "blocks-based API (including dispatch I/O) will be "
                    "disabled.")

elseif (DISPATCH_USE_PRIVATE_BLOCKSRUNTIME)
    set(blocks_install_prefix
        "${CMAKE_CURRENT_BINARY_DIR}/thirdparty/blocksRuntime-subproject")
    dispatch_add_subproject(blocksRuntime
        SOURCE_DIR thirdparty/libBlocksRuntime
        INSTALL_PREFIX "${blocks_install_prefix}"
        LIBRARY lib/libBlocksRuntime.a
        INCLUDE_DIR include/Blocks)

    install(FILES "${blocks_install_prefix}/lib/libBlocksRuntime.a"
        DESTINATION "${CMAKE_INSTALL_LIBDIR}"
        RENAME libdispatch_BlocksRuntime.a
    )
    install(FILES "${blocks_install_prefix}/include/Blocks/Block.h"
        DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
    )
elseif (DISPATCH_ENABLE_BLOCKS)
    find_package(BlocksRuntime)
    if (NOT BLOCKSRUNTIME_FOUND)
        set(DISPATCH_ENABLE_BLOCKS FALSE)
        message(WARNING "A blocks runtime was not found; support for "
                        "blocks-based API (including dispatch I/O) will be "
                        "disabled.")
    endif ()
endif ()

if (DISPATCH_ENABLE_BLOCKS)
    add_definitions(-fblocks)
elseif (COMPILER_SUPPORTS_BLOCKS AND NOT DISPATCH_ENABLE_BLOCKS)
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
