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
if (NOT DISPATCH_SANITIZE)
    target_link_libraries(libdispatch_shared LINK_PRIVATE -Wl,-z,defs)
endif ()

################################################################################
## STATIC_LIB
set_property(TARGET libdispatch_static APPEND PROPERTY COMPILE_FLAGS -fPIC)
target_link_libraries(libdispatch_static LINK_PUBLIC -pthread rt)

set (supplemental_libs)
if (NOT DISPATCH_SYSTEM_KQUEUE)
    list(APPEND supplemental_libs ${KQUEUE_LIBRARIES})
endif ()
if (NOT DISPATCH_SYSTEM_PTHREAD_WORKQUEUE)
    list(APPEND supplemental_libs ${PTHREAD_WORKQUEUE_LIBRARIES})
endif ()
if (NOT DISPATCH_SYSTEM_BLOCKS_RUNTIME)
    list(APPEND supplemental_libs ${BLOCKSRUNTIME_LIBRARIES})
endif ()

file(READ "${dispatch_SOURCE_DIR}/scripts/libdispatch_globals.regex"
     globals_regex)
string(STRIP "${globals_regex}" globals_regex)

dispatch_partial_link(libdispatch_static ${supplemental_libs}
    KEEP_GLOBAL_REGEX "${globals_regex}"
)

target_link_libraries(libdispatch_static LINK_PUBLIC
    ${BLOCKSRUNTIME_LIBRARIES} rt -pthread
)
################################################################################
## INSTALLATION
install(
    TARGETS libdispatch_shared libdispatch_static
    ARCHIVE DESTINATION "${DISPATCH_INSTALL_LIB_DIR}"
    LIBRARY DESTINATION "${DISPATCH_INSTALL_LIB_DIR}"
)
