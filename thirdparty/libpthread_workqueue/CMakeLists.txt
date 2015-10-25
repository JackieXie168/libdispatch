#
# Copyright (c) 2011 Marius Zwicker <marius@mlba-team.de>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

cmake_minimum_required(VERSION 2.8.7)
project(pthread_workqueue C)

include(CheckIncludeFile)

if (NOT CMAKE_BUILD_TYPE)
    set (CMAKE_BUILD_TYPE Release)
endif ()

if (CMAKE_SYSTEM_NAME MATCHES Linux)
    set (LINUX 1)
endif ()

#///////////////////////////////////////////////////////////////////////////////
#files
file(GLOB_RECURSE headers include/*.h)
source_group(Headers FILES ${headers})

file(GLOB sources src/*.h src/*.c)

include_directories(include src)
include_directories(${CMAKE_CURRENT_BINARY_DIR})

if(WIN32)
    file(GLOB win32_sources src/windows/*.h src/windows/*.c)
    list(APPEND sources "${win32_sources}")

    add_definitions(-D_USRDLL -D_WINDLL)
endif ()

if (UNIX)
    file(GLOB posix_sources src/posix/*.h src/posix/*.c)
    list(APPEND sources "${posix_sources}")

    add_definitions(-D_GNU_SOURCE)
    add_definitions(-std=c99 -fvisibility=hidden
        -Wall -Wextra -Wmissing-prototypes)
    if (CMAKE_BUILD_TYPE MATCHES Release)
        # We always want debug symbols.
        add_definitions(-g)
    endif ()
endif ()

if (LINUX)
    file(GLOB linux_sources src/linux/*.h src/linux/*.c)
    list(APPEND sources ${linux_sources})
endif ()

source_group(Sources FILES ${sources})

#///////////////////////////////////////////////////////////////////////////////

check_include_file(err.h HAVE_ERR_H)
set(CONFIG_EPILOGUE
"
#if _WIN32
#define PWQ_EXPORT extern __declspec(dllexport)
#else
#define PWQ_EXPORT extern __attribute__((visibility(\"default\")))
#endif
")
configure_file(config/config.h.in "${CMAKE_CURRENT_BINARY_DIR}/config/config.h")

add_library(pthread_workqueue_static STATIC ${sources} ${headers})
if (NOT WIN32)
    set_property(TARGET pthread_workqueue_static APPEND PROPERTY
        COMPILE_FLAGS -fPIC)
endif ()

add_library(pthread_workqueue_shared SHARED ${sources} ${headers})
set_target_properties(pthread_workqueue_shared PROPERTIES
    SOVERSION 0 VERSION 0.9.2)

foreach (target pthread_workqueue_shared pthread_workqueue_static)
    if (UNIX)
        target_link_libraries(${target} -pthread)
    endif ()
    if(LINUX)
        target_link_libraries(${target} rt)
    endif()
    set_target_properties(${target} PROPERTIES
        DEBUG_POSTFIX "D"
        OUTPUT_NAME pthread_workqueue)
endforeach()

#///////////////////////////////////////////////////////////////////////////////
#tests
add_subdirectory(testing)

install(TARGETS pthread_workqueue_static pthread_workqueue_shared
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib)

install(FILES ${headers} DESTINATION include)
