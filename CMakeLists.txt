cmake_minimum_required(VERSION 2.8.12)

project (dispatch)
set (DISPATCH_VERSION 0.1.3.1)
set (DISPATCH_VERSION_MAJOR 0)
set (DISPATCH_VERSION_MINOR 1)
set (DISPATCH_VERSION_PATCH 3)
set (DISPATCH_VERSION_TWEAK 1)

set (DISPATCH_ABI_VERSION 1)

list (APPEND CMAKE_MODULE_PATH "${dispatch_SOURCE_DIR}/cmake")
include (BuildUtil)

include (CheckCCompilerFlag)
include (CheckCSourceCompiles)
include (CMakePushCheckState)

enable_testing()

set (CPACK_PACKAGE_NAME "libdispatch")
set (CPACK_PACKAGE_DESCRIPTION_SUMMARY "Linux port of Apple's open-source concurrency library")
set (CPACK_PACKAGE_VERSION "${DISPATCH_VERSION}")
set (CPACK_PACKAGE_VERSION_MAJOR "${DISPATCH_VERSION_MAJOR}")
set (CPACK_PACKAGE_VERSION_MINOR "${DISPATCH_VERSION_MINOR}")
set (CPACK_PACKAGE_VERSION_PATCH "${DISPATCH_VERSION_PATCH}")
set (CPACK_RESOURCE_FILE_LICENSE "${dispatch_SOURCE_DIR}/LICENSE")
set (CPACK_RESOURCE_FILE_README "${dispatch_SOURCE_DIR}/README.md")
set (CPACK_PACKAGE_CONTACT "Libdispatch for Linux Maintainers.")
set (CPACK_PACKAGE_VENDOR "Libdispatch for Linux Maintainers.")
set (CPACK_GENERATOR TGZ CACHE STRING "Installer types to generate.  Sensible options include TGZ, RPM and DEB")
set (CPACK_PACKAGE_INSTALL_DIRECTORY "CMake ${CMake_VERSION_MAJOR}.${CMake_VERSION_MINOR}")
set (CPACK_SOURCE_GENERATOR TGZ)
set (CPACK_DEBIAN_PACKAGE_DEPENDS "libc6 (>=2.7), libblocksruntime0 (>=0.1), libpthread-workqueue0 (>=0.8), libkqueue0 (>=1.0)")
include (CPack)

#///////////////////////////////////////////////////////////////////////////////
if (NOT CMAKE_BUILD_TYPE)
    set (CMAKE_BUILD_TYPE Release)
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

if (DISPATCH_SANITIZE)
    add_compile_options(-fsanitize=${DISPATCH_SANITIZE} -fno-omit-frame-pointer)
    set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -fsanitize=${DISPATCH_SANITIZE}")
    set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -fsanitize=${DISPATCH_SANITIZE}")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=${DISPATCH_SANITIZE}")
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
check_c_compiler_flag(-momit-leaf-frame-pointer SUPPORTS_MOMIT_LEAF_FRAME_POINTER)

if (NOT COMPILER_HAS_BLOCKS_SUPPORT)
    message(WARNING "Blocks compiler support was not found; dispatch i/o "
                    "will not be built.")
endif ()

#///////////////////////////////////////////////////////////////////////////////
# Find functions and declarations we care about.

dispatch_check_decls(CLOCK_UPTIME CLOCK_MONOTONIC INCLUDES time.h)
dispatch_check_decls(NOTE_NONE NOTE_REAP NOTE_SIGNAL NOTE_REVOKE
    INCLUDES sys/event.h)
dispatch_check_decls(TAILQ_FOREACH_SAFE INCLUDES sys/queue.h)
dispatch_check_decls(FD_COPY INCLUDES sys/select.h)
dispatch_check_decls(SIGEMT INCLUDES signal.h)
dispatch_check_decls(VQ_UPDATE VQ_VERYLOWDISK INCLUDES sys/mount.h)
dispatch_check_decls(POSIX_SPAWN_SETEXEC POSIX_SPAWN_START_SUSPENDED
    INCLUDES sys/spawn.h)

cmake_push_check_state ()
    set (CMAKE_REQUIRED_DEFINITIONS -D_GNU_SOURCE)
    dispatch_check_decls(program_invocation_short_name INCLUDES errno.h)
cmake_pop_check_state ()

dispatch_check_funcs(pthread_key_init_np pthread_main_np
     sysctlbyname sysconf getprogname
     strlcpy asprintf)

dispatch_check_headers(sys/cdefs.h unistd.h)

if (HAVE_UNISTD_H AND COMPILER_HAS_BLOCKS_SUPPORT)
    cmake_push_check_state()
        set(CMAKE_REQUIRED_DEFINITIONS -D_GNU_SOURCE)
        set(CMAKE_REQUIRED_FLAGS -fblocks)
        check_c_source_compiles("#include <unistd.h>\nint main(){}"
            HAS_WORKING_UNISTD_H)
    cmake_pop_check_state()
    if (NOT HAS_WORKING_UNISTD_H)
        set (HAS_PROBLEMATIC_UNISTD_H 1)
    endif ()
endif ()


set (USE_FUTEX_SEM 1)

configure_file("config/config.h.cmake.in"
    "${dispatch_BINARY_DIR}/config/config.h"
    @ONLY
)

add_compile_options(
    -Wall
    -Wextra
    -Wno-unused-parameter

    -fvisibility=hidden
)

if (COMPILER_HAS_BLOCKS_SUPPORT)
    add_compile_options(-fblocks)
endif ()

if (SUPPORTS_MOMIT_LEAF_FRAME_POINTER)
    add_compile_options(-momit-leaf-frame-pointer)
endif ()

if (CMAKE_C_COMPILER_ID MATCHES "GNU")
    add_compile_options(-Wno-unknown-pragmas)
endif ()

#///////////////////////////////////////////////////////////////////////////////

include_directories(SYSTEM fixincludes)

add_subdirectory(src)
add_subdirectory(testing)

# Install man pages
add_subdirectory(man)

# Install public headers
add_subdirectory(dispatch)
add_subdirectory(os)

