# testing/CMakeLists.txt
################################################################################
if (NOT CMAKE_VERSION VERSION_LESS 3.2)
    set (USES_TERMINAL_FLAG USES_TERMINAL)
else ()
    set (USES_TERMINAL_FLAG "")
endif ()

# Aggregate target that collects all the test executables.
add_custom_target(check
    COMMAND py.test "${CMAKE_CURRENT_SOURCE_DIR}" -rsx
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
    VERBATIM ${USES_TERMINAL_FLAG})

#///////////////////////////////////////////////////////////////////////////////

execute_process(
    # Give the test suite access to dispatch's private headers.
    COMMAND "${CMAKE_COMMAND}" -E create_symlink
        "${dispatch_SOURCE_DIR}/private"
        "${CMAKE_CURRENT_BINARY_DIR}/dispatch"
)

include_directories(
    ${dispatch_BINARY_DIR}
    ${dispatch_SOURCE_DIR}

    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_BINARY_DIR}

    ${KQUEUE_INCLUDE_DIRS}
    ${BLOCKSRUNTIME_INCLUDE_DIRS}
)

add_library(bsdtests SHARED
    bsdtests.c
    bsdtests.h
    dispatch_test.c
    dispatch_test.h
    shims.h
    shims/asprintf.c
    shims/asprintf.h
    shims/arc4random.c
    shims/arc4random.h
    shims/fgetln.c
    shims/fgetln.h
)
target_link_libraries(bsdtests
    LINK_PUBLIC ${BLOCKSRUNTIME_LIBRARIES} -lm
    LINK_PRIVATE libdispatch_shared ${KQUEUE_LIBRARIES} -pthread
)

function (dispatch_test test_name)
    if (ARGN)
        set (sources "${ARGN}")
    else ()
        set (sources "${test_name}.c")
    endif ()

    add_executable("${test_name}" ${sources})
    add_dependencies(check "${test_name}")
    target_link_libraries("${test_name}" libdispatch_shared bsdtests)
endfunction ()

add_definitions(
    -Wall
    -Wextra
    -Wno-unused-parameter
    -fblocks
)

add_executable(bsdtestharness bsdtestharness.c)
add_executable(bsdtestsummarize bsdtestsummarize.c)
foreach (target bsdtestharness bsdtestsummarize)
    target_link_libraries("${target}" libdispatch_shared bsdtests)
endforeach ()

add_dependencies(check bsdtestharness bsdtestsummarize)

dispatch_test( dispatch_after )
dispatch_test( dispatch_api )
dispatch_test( dispatch_apply )
dispatch_test( dispatch_c99 )
dispatch_test( dispatch_cascade )
dispatch_test( dispatch_concur )
dispatch_test( dispatch_context_for_key )
dispatch_test( dispatch_data )
dispatch_test( dispatch_debug )
dispatch_test( dispatch_drift )
dispatch_test( dispatch_group )
dispatch_test( dispatch_io )
dispatch_test( dispatch_io_net )
dispatch_test( dispatch_main_queue )
dispatch_test( dispatch_np )
dispatch_test( dispatch_overcommit )
dispatch_test( dispatch_pingpong )
dispatch_test( dispatch_plusplus dispatch_plusplus.cpp)
dispatch_test( dispatch_priority )

dispatch_test( dispatch_priority2 dispatch_priority.c )
set_target_properties(dispatch_priority2 PROPERTIES
    COMPILE_DEFINITIONS USE_SET_TARGET_QUEUE=1)

dispatch_test( dispatch_proc )
dispatch_test( dispatch_queue_finalizer )
dispatch_test( dispatch_read )
dispatch_test( dispatch_read2 )
dispatch_test( dispatch_readsync )
dispatch_test( dispatch_select )
dispatch_test( dispatch_sema )
dispatch_test( dispatch_starfish )
dispatch_test( dispatch_suspend_timer )
dispatch_test( dispatch_timer )
dispatch_test( dispatch_timer_bit31 )
dispatch_test( dispatch_timer_bit63 )
dispatch_test( dispatch_timer_set_time )
dispatch_test( dispatch_timer_short )
dispatch_test( dispatch_timer_timeout )
dispatch_test( dispatch_vm )
dispatch_test( dispatch_vnode )

