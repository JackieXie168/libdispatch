set (sources
    allocator.c
    apply.c
    benchmark.c
    init.c
    introspection.c
    object.c
    once.c
    queue.c
    semaphore.c
    source.c
    time.c
)

if (COMPILER_HAS_BLOCKS_SUPPORT)
    list (APPEND sources
        data.c
        io.c
        transform.c
    )
    add_definitions (-fblocks)
endif ()

include_directories (
    "${dispatch_SOURCE_DIR}"
    "${dispatch_BINARY_DIR}"
    "${dispatch_SOURCE_DIR}/private"
    "${dispatch_SOURCE_DIR}/os"

    ${KQUEUE_INCLUDE_DIRS}
    ${PTHREAD_WORKQUEUE_INCLUDE_DIRS}
    ${BLOCKSRUNTIME_INCLUDE_DIRS}
)

add_definitions(
    -Wall
    -Wextra
    -fvisibility=hidden
)

if (CMAKE_C_COMPILER_ID MATCHES Clang)
    add_definitions(
        -Weverything
        -Wno-language-extension-token
        -Wno-undef
        -Wno-pedantic
        -Wno-cast-align
        -Wno-vla
        -Wno-padded
        -Wno-bad-function-cast
        -Wno-missing-noreturn
        -Wno-format-nonliteral
        -Wno-unreachable-code
        -Wno-documentation
        -Wno-disabled-macro-expansion
    )
endif ()

if (CMAKE_C_COMPILER_ID MATCHES "GNU")
    add_definitions(-Wno-unknown-pragmas)
endif ()

add_library(libdispatch_static STATIC ${sources})
add_library(libdispatch_shared SHARED ${sources})

foreach (target libdispatch_shared libdispatch_static)
    target_link_libraries(${target}
        ${PTHREAD_WORKQUEUE_LIBRARIES}
        ${KQUEUE_LIBRARIES}
        ${BLOCKSRUNTIME_LIBRARIES}
        rt
        -pthread
    )
    if (NOT DISPATCH_SANITIZE)
        target_link_libraries(${target} -Wl,-z,defs)
    endif ()
endforeach ()

set_target_properties(libdispatch_shared libdispatch_static PROPERTIES
    VERSION ${DISPATCH_VERSION}
    SOVERSION ${DISPATCH_ABI_VERSION}
    OUTPUT_NAME dispatch
)

install(
    TARGETS libdispatch_shared libdispatch_static
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
)
