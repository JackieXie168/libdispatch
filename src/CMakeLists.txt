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

add_library(libdispatch_shared SHARED ${sources})
add_library(libdispatch_static STATIC ${sources})
set_target_properties(libdispatch_static libdispatch_shared PROPERTIES
    OUTPUT_NAME dispatch)

################################################################################
## SHARED LIB
set_target_properties(libdispatch_shared PROPERTIES
    VERSION ${DISPATCH_VERSION} SOVERSION ${DISPATCH_ABI_VERSION})

set(version_script
    "${dispatch_SOURCE_DIR}/scripts/libdispatch_globals.version")
dispatch_add_file_dependencies(libdispatch_shared "${version_script}")

target_link_libraries(libdispatch_shared LINK_PRIVATE
    ${PTHREAD_WORKQUEUE_LIBRARIES}
    ${KQUEUE_LIBRARIES}
    ${BLOCKSRUNTIME_LIBRARIES}
    rt
    -pthread
    "-Wl,--version-script,${version_script}"
)

################################################################################
## STATIC_LIB
set_property(TARGET libdispatch_static APPEND PROPERTY COMPILE_FLAGS -fPIC)
target_link_libraries(libdispatch_static LINK_PUBLIC -pthread rt)

set (partial_link_libs "")
if (DISPATCH_USE_PRIVATE_KQUEUE)
    list(APPEND partial_link_libs ${KQUEUE_LIBRARIES})
else ()
    target_link_libraries(libdispatch_static LINK_PRIVATE
        ${KQUEUE_LIBRARIES})
endif ()

if (DISPATCH_USE_PRIVATE_PTHREAD_WORKQUEUE)
    list(APPEND partial_link_libs ${PTHREAD_WORKQUEUE_LIBRARIES})
elseif (DISPATCH_ENABLE_PTHREAD_WORKQUEUE)
    target_link_libraries(libdispatch_static LINK_PRIVATE
        ${PTHREAD_WORKQUEUE_LIBRARIES})
endif ()

if (DISPATCH_USE_PRIVATE_BLOCKSRUNTIME)
    list(APPEND partial_link_libs ${BLOCKSRUNTIME_LIBRARIES})
elseif (DISPATCH_ENABLE_BLOCKS)
    target_link_libraries(libdispatch_static LINK_PRIVATE
        ${BLOCKSRUNTIME_LIBRARIES})
endif ()

file(READ "${dispatch_SOURCE_DIR}/scripts/libdispatch_globals.regex"
     globals_regex)
string(STRIP "${globals_regex}" globals_regex)

dispatch_partial_link(libdispatch_static ${partial_link_libs}
    GLOBAL_SYMBOL_REGEX "${globals_regex}"
)

################################################################################
## INSTALLATION
install(
    TARGETS libdispatch_shared libdispatch_static
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
)
