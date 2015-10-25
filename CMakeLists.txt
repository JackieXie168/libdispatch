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

project(kqueue C)

set(KQUEUE_VERSION 2.0.4)
set(KQUEUE_ABI_VERSION 0)

if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif ()

include(config/config.cmake)
configure_file(config/config.h.in "${CMAKE_CURRENT_BINARY_DIR}/config/config.h")


#files
file(GLOB_RECURSE INCL include/*.h)
source_group(includes FILES ${INCL})

if(WIN32)
    file(GLOB SRC
        src/windows/*.h
        src/windows/*.c
        src/common/*.h
        src/*.c
        src/common/map.c
        src/common/filter.c
        src/common/knote.c
        src/common/kevent.c
        src/common/kqueue.c
    )
    add_definitions(
        -D_USRDLL
        -D_WINDLL
    )
    if(MINGW)
        SET(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG}  -march=i486")
        SET(CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE} -march=i486")
    endif()
else()
    file(GLOB SRC
        src/posix/*.h
        src/posix/platform.c
        src/linux/*.h
        src/linux/platform.c
        src/linux/signal.c
        src/linux/socket.c
        src/linux/timer.c
        src/linux/user.c
        src/linux/vnode.c
        src/linux/write.c
        src/linux/read.c
        src/common/*.h
        src/common/filter.c
        src/common/knote.c
        src/common/map.c
        src/common/kevent.c
        src/common/kqueue.c
    )
    include_directories(
        src/common
    )
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -std=c99")
    add_definitions(
        -Wall -Wextra
        -Wno-missing-field-initializers
        -fPIC
        -D_XOPEN_SOURCE=600
        -D_GNU_SOURCE
        -fvisibility=hidden
    )
    if (CMAKE_BUILD_TYPE MATCHES Release)
        # Always add debug symbols
        add_definitions(-g)
    endif ()
endif()
source_group(src FILES ${SRC})

#includes
include_directories( include )
include_directories("${CMAKE_CURRENT_BINARY_DIR}")

#library (static or shared)
add_library(kqueue_shared STATIC ${SRC} ${INCL})
add_library(kqueue_static SHARED ${SRC} ${INCL})

set_target_properties(kqueue_shared kqueue_static PROPERTIES
    OUTPUT_NAME kqueue
    SOVERSION ${KQUEUE_ABI_VERSION}
    VERSION ${KQUEUE_VERSION}
)

foreach(target kqueue_shared kqueue_static)
    if(WIN32)
        target_link_libraries(${target} ws2_32)
    endif()
    if (UNIX)
        target_link_libraries(${target} -pthread)
    endif ()
endforeach ()

#tests
option(KQUEUE_ENABLE_TEST_SUITE "Enable to build tests for libkqueue" FALSE)
if(KQUEUE_ENABLE_TEST_SUITE)
    message("-- Adding tests for libkqueue")
    add_subdirectory(test)
endif()

install(TARGETS kqueue_shared kqueue_static
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)
install(DIRECTORY include/ DESTINATION include/kqueue)
