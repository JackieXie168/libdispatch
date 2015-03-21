set (sources
    apply.c
    benchmark.c
    init.c
    object.c
    once.c
    queue.c
    semaphore.c
    source.c
    time.c
)

if (DISPATCH_ENABLE_BLOCKS)
    list (APPEND sources
        data.c
        io.c
        transform.c
    )
endif ()

include_directories (
    "${dispatch_SOURCE_DIR}"
    "${dispatch_BINARY_DIR}"
    "${dispatch_SOURCE_DIR}/private"
    "${dispatch_SOURCE_DIR}/os"

    ${KQUEUE_INCLUDE_DIRS}
)

if (DISPATCH_ENABLE_PTHREAD_WORKQUEUE)
    include_directories(${PTHREAD_WORKQUEUE_INCLUDE_DIRS})
endif ()
if (DISPATCH_ENABLE_BLOCKS)
    include_directories(${BLOCKSRUNTIME_INCLUDE_DIRS})
endif ()

add_definitions(
    -Wall
    -Wextra
    -Wno-unused-parameter
    -fvisibility=hidden
)

if (CMAKE_C_COMPILER_ID MATCHES "GNU")
    add_definitions(-Wno-unknown-pragmas)
endif ()

add_library(libdispatch_static STATIC ${sources})
add_library(libdispatch_shared SHARED ${sources})

foreach (target libdispatch_shared libdispatch_static)
    if (DISPATCH_ENABLE_BLOCKS)
        target_link_libraries("${target}" LINK_PUBLIC ${BLOCKSRUNTIME_LIBRARIES})
    endif ()
    if (DISPATCH_ENABLE_PTHREAD_WORKQUEUE)
        target_link_libraries("${target}" LINK_PRIVATE ${PTHREAD_WORKQUEUE_LIBRARIES})
    endif ()
    target_link_libraries(${target} LINK_PRIVATE
        ${KQUEUE_LIBRARIES}
        -lrt
        -pthread
    )
endforeach ()

set_target_properties(libdispatch_shared libdispatch_static PROPERTIES
    VERSION ${DISPATCH_VERSION}
    SOVERSION ${DISPATCH_ABI_VERSION}
    OUTPUT_NAME dispatch
)
set_property(TARGET libdispatch_static APPEND PROPERTY COMPILE_FLAGS -fPIC)

install(
    TARGETS libdispatch_shared libdispatch_static
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
)
