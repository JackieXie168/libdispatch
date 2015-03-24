cmake_minimum_required(VERSION 2.8.7)

project (dispatch)
set (DISPATCH_VERSION 0.2.git)
set (DISPATCH_ABI_VERSION 1)

list (APPEND CMAKE_MODULE_PATH "${dispatch_SOURCE_DIR}/cmake")
include (BuildUtil)

include (CheckPrototypeDefinition)
include (CheckCCompilerFlag)
include (CheckTypeSize)
include (CheckCSourceCompiles)
include (CMakePushCheckState)
include (GNUInstallDirs)

set(DISPATCH_INSTALL_INCLUDE_DIR "${CMAKE_INSTALL_INCLUDEDIR}/dispatch")
set(DISPATCH_INSTALL_LIB_DIR "${CMAKE_INSTALL_LIBDIR}")
set(DISPATCH_INSTALL_MAN_DIR "${CMAKE_INSTALL_MANDIR}")

if (POLICY CMP0022)
    cmake_policy(SET CMP0022 OLD)
endif ()

#///////////////////////////////////////////////////////////////////////////////
if (NOT CMAKE_BUILD_TYPE)
    set (CMAKE_BUILD_TYPE MinSizeRel)
endif ()

#///////////////////////////////////////////////////////////////////////////////
option (DISPATCH_ENABLE_TEST_SUITE "Whether to build the test suite" NO)

option (DISPATCH_USE_LIBDISPATCH_INIT_CONSTRUCTOR
    "Use libdispatch_init as a constructor" YES)
set(USE_LIBDISPATCH_INIT_CONSTRUCTOR
    ${DISPATCH_USE_LIBDISPATCH_INIT_CONSTRUCTOR})
#///////////////////////////////////////////////////////////////////////////////
set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=gnu99")
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=gnu++98")
add_definitions(-D_GNU_SOURCE)

# Defines and compile flags
if (CMAKE_BUILD_TYPE MATCHES Debug)
    add_definitions(-DDISPATCH_DEBUG=1)
endif ()

if (CMAKE_C_COMPILER_ID MATCHES Clang)
    add_definitions( -fcolor-diagnostics )
endif ()

if (DISPATCH_SANITIZE)
    add_definitions(-g -fsanitize=${DISPATCH_SANITIZE})
    link_libraries(-fsanitize=${DISPATCH_SANITIZE})
endif ()

if (DISPATCH_VERSION MATCHES git)
    set( DISPATCH_GIT_REF "" )
    execute_process(
        COMMAND git rev-parse --short HEAD
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        OUTPUT_VARIABLE DISPATCH_GIT_REF
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    if (DISPATCH_GIT_REF)
        string( REPLACE "git" "${DISPATCH_GIT_REF}"
            DISPATCH_BUILD_STRING "${DISPATCH_VERSION}" )
    endif ()
else ()
    set( DISPATCH_BUILD_STRING "${DISPATCH_VERSION}" )
endif ()

#///////////////////////////////////////////////////////////////////////////////
# Find/build libraries we will need

if (NOT DISPATCH_SYSTEM_KQUEUE)
    dispatch_add_subproject(kqueue
        SOURCE_DIR thirdparty/libkqueue
        INSTALL_PREFIX thirdparty/kqueue-subproject
        LIBRARY lib/libkqueue.a
        INCLUDE_DIR include/kqueue
    )
else ()
    find_package(kqueue REQUIRED)
    cmake_push_check_state()
        set( CMAKE_REQUIRED_INCLUDES "${KQUEUE_INCLUDE_DIRS}" )
        set( CMAKE_REQUIRED_LIBRARIES "${KQUEUE_LIBRARIES}" )
        dispatch_check_decls(
            EV_SET64 NOTE_NONE NOTE_REAP NOTE_REVOKE NOTE_SIGNAL
            NOTE_LEEWAY NOTE_NSECONDS NOTE_ABSOLUTE
            INCLUDES sys/event.h
        )
        check_type_size("struct kevent64_s" DECL_KEVENT64_S)
        dispatch_check_funcs( kevent64 )
    cmake_pop_check_state()
endif()

if (NOT DISPATCH_SYSTEM_PTHREAD_WORKQUEUE)
    dispatch_add_subproject(pthread_workqueue
        SOURCE_DIR thirdparty/libpthread_workqueue
        INSTALL_PREFIX thirdparty/pthread_workqueue-subproject
        LIBRARY lib/libpthread_workqueue.a
        LIBRARY_DEBUG lib/libpthread_workqueueD.a
    )
else ()
    find_package(pthread_workqueue REQUIRED)
    dispatch_search_libs(pthread_workqueue_setdispatch_np LIBRARIES
        "${PTHREAD_WORKQUEUE_LIBRARIES}")
endif ()

if (NOT DISPATCH_SYSTEM_BLOCKS_RUNTIME)
    set(blocks_install_prefix
        "${CMAKE_CURRENT_BINARY_DIR}/thirdparty/blocksRuntime-subproject")
    dispatch_add_subproject(blocksRuntime
        SOURCE_DIR thirdparty/libBlocksRuntime
        INSTALL_PREFIX "${blocks_install_prefix}"
        LIBRARY lib/libBlocksRuntime.a
        INCLUDE_DIR include/Blocks
    )

    install(FILES "${blocks_install_prefix}/lib/libBlocksRuntime.a"
        DESTINATION "${DISPATCH_INSTALL_LIB_DIR}"
        RENAME libdispatch_BlocksRuntime.a
    )
    install(FILES "${blocks_install_prefix}/include/Blocks/Block.h"
        DESTINATION "${DISPATCH_INSTALL_INCLUDE_DIR}"
    )
else ()
    find_package(BlocksRuntime REQUIRED)
endif ()

#///////////////////////////////////////////////////////////////////////////////

check_c_compiler_flag(-fblocks COMPILER_HAS_BLOCKS_SUPPORT)
if (NOT COMPILER_HAS_BLOCKS_SUPPORT)
    message(WARNING "Blocks compiler support was not found; dispatch i/o "
                    "will not be built.")
endif ()

dispatch_check_decls(F_RDADVISE INCLUDES fcntl.h)
dispatch_check_decls(CLOCK_UPTIME CLOCK_MONOTONIC INCLUDES time.h)
dispatch_check_decls(VQ_UPDATE VQ_VERYLOWDISK INCLUDES sys/mount.h)
dispatch_check_decls(TAILQ_FOREACH_SAFE INCLUDES sys/queue.h)
dispatch_check_decls(FD_COPY INCLUDES sys/select.h)
dispatch_check_decls(SIGEMT INCLUDES signal.h)
dispatch_check_decls(POSIX_SPAWN_SETEXEC POSIX_SPAWN_START_SUSPENDED
    INCLUDES sys/spawn.h)

cmake_push_check_state ()
    set (CMAKE_REQUIRED_DEFINITIONS -D_GNU_SOURCE)
    dispatch_check_decls(program_invocation_short_name INCLUDES errno.h)
cmake_pop_check_state ()

dispatch_check_funcs(
    arc4random
    asprintf
    fgetln
    getprogname
    issetugid
    mach_absolute_time
    malloc_create_zone
    posix_fadvise
    pthread_key_init_np
    pthread_main_np
    strlcpy
    sysconf
    sysctlbyname
    vasprintf
)

dispatch_check_headers(
    CoreFoundation/CoreFoundation.h
    crt_externs.h
    fcntl.h
    libkern/OSAtomic.h
    libkern/OSByteOrder.h
    libkern/OSCrossEndian.h
    libproc/internal.h
    malloc/malloc.h
    pthread_machdep.h
    pthread_np.h
    sys/cdefs.h
    sys/guarded.h
    TargetConditionals.h
    unistd.h
)

if (HAVE_UNISTD_H AND COMPILER_HAS_BLOCKS_SUPPORT)
    cmake_push_check_state()
        set(CMAKE_REQUIRED_DEFINITIONS -D_GNU_SOURCE)
        set(CMAKE_REQUIRED_FLAGS -fblocks)
        check_c_source_compiles("#include <unistd.h>\nint main(){}"
            HAVE_WORKING_UNISTD_H)
    cmake_pop_check_state()
    if (NOT HAVE_WORKING_UNISTD_H)
        set (HAVE_PROBLEMATIC_UNISTD_H 1)
    endif ()
endif ()

# Test if __builtin_ffs() takes a signed argument.
cmake_push_check_state()
    check_c_source_compiles("int __builtin_ffs(int); int main(){}"
        HAVE_WORKING_BUILTIN_FFS)
cmake_pop_check_state()
if (NOT HAVE_WORKING_BUILTIN_FFS)
    set( HAVE_PROBLEMATIC_BUILTIN_FFS 1 )
endif ()

set( HAVE_PTHREAD_WORKQUEUES 1 )
set( USE_POSIX_SEM 1 )

configure_file("config/config.h.cmake.in"
    "${dispatch_BINARY_DIR}/config/config.h"
    @ONLY
)

#///////////////////////////////////////////////////////////////////////////////

include_directories(SYSTEM fixincludes)

add_subdirectory(src)
add_subdirectory(testing)

# Install man pages
add_subdirectory(man)

# Install public headers
add_subdirectory(dispatch)
add_subdirectory(os)
