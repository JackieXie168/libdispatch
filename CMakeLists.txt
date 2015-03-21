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
# Find libraries we will need

find_package(kqueue REQUIRED)
find_package(pthread_workqueue)
find_package(BlocksRuntime)

set (HAVE_PTHREAD_WORKQUEUES "${PTHREAD_WORKQUEUE_FOUND}")
dispatch_search_libs(pthread_workqueue_setdispatch_np LIBRARIES
    "${PTHREAD_WORKQUEUE_LIBRARIES}")

check_c_compiler_flag(-fblocks COMPILER_HAS_BLOCKS_SUPPORT)
check_c_compiler_flag("-momit-leaf-frame-pointer"
    SUPPORTS_MOMIT_LEAF_FRAME_POINTER)

if (NOT COMPILER_HAS_BLOCKS_SUPPORT)
    message(WARNING "Blocks compiler support was not found; dispatch i/o "
                    "will not be built.")
endif ()

#///////////////////////////////////////////////////////////////////////////////
dispatch_check_decls(F_RDADVISE INCLUDES fcntl.h)
dispatch_check_decls(CLOCK_UPTIME CLOCK_MONOTONIC INCLUDES time.h)
dispatch_check_decls(NOTE_NONE NOTE_REAP NOTE_SIGNAL NOTE_REVOKE
    INCLUDES sys/event.h)
dispatch_check_decls(VQ_UPDATE VQ_VERYLOWDISK INCLUDES sys/mount.h)
dispatch_check_decls(TAILQ_FOREACH_SAFE INCLUDES sys/queue.h)
dispatch_check_decls(FD_COPY INCLUDES sys/select.h)
dispatch_check_decls(SIGEMT INCLUDES signal.h)
dispatch_check_decls(POSIX_SPAWN_SETEXEC POSIX_SPAWN_START_SUSPENDED
    INCLUDES sys/spawn.h)

if (KQUEUE_INCLUDE_DIRS AND KQUEUE_LIBRARIES)
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
endif ()

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

check_c_compiler_flag("-fvisibility=hidden" SUPPORTS_FVISIBILITY_HIDDEN)
if (SUPPORTS_FVISIBILITY_HIDDEN)
    set (VISIBILITY_FLAGS "-fvisibility=hidden")
endif ()

# Test if __builtin_ffs() takes a signed argument.
cmake_push_check_state()
    check_c_source_compiles("int __builtin_ffs(int); int main(){}"
        HAVE_WORKING_BUILTIN_FFS)
cmake_pop_check_state()
if (NOT HAVE_WORKING_BUILTIN_FFS)
    set( HAVE_PROBLEMATIC_BUILTIN_FFS 1 )
endif ()

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
