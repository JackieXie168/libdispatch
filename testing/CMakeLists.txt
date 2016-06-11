# testing/CMakeLists.txt
################################################################################

if (NOT DISPATCH_ENABLE_TEST_SUITE)
    return ()
endif ()

if (NOT COMPILER_HAS_BLOCKS_SUPPORT)
    message(WARNING
        "No compiler support for Blocks; test suite will not be built.")
    return ()
endif ()

execute_process(
    # Give the test suite access to dispatch's private headers.
    COMMAND "${CMAKE_COMMAND}" -E create_symlink
        "${dispatch_SOURCE_DIR}/private"
        "${CMAKE_CURRENT_BINARY_DIR}/dispatch"
)

execute_process(
    # Check that pytest is installed.
    COMMAND py.test --version
    RESULT_VARIABLE exit_status
    ERROR_QUIET
)

if (${exit_status} EQUAL 0)
    add_test(
        NAME dispatch_pytest
        COMMAND py.test "${CMAKE_CURRENT_SOURCE_DIR}" -rsx
    )
else ()
    message(WARNING "Skipping dispatch_pytest because pytest was not found")
endif ()

add_library(bsdtests STATIC
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

target_include_directories(bsdtests PRIVATE ${KQUEUE_INCLUDE_DIRS})
target_link_libraries(bsdtests PRIVATE libdispatch_shared ${KQUEUE_LIBRARIES})

function (dispatch_test test_name)
    if (ARGN)
        set (sources "${ARGN}")
    else ()
        set (sources "${test_name}")
    endif ()

    add_executable("${test_name}" ${sources})
    add_test(NAME "${test_name}" COMMAND "${test_name}")
endfunction ()

link_libraries(libdispatch_shared ${BLOCKS_RUNTIME_LIBRARIES} m bsdtests)

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_BINARY_DIR}
)

include_directories(SYSTEM
    ${BLOCKS_RUNTIME_INCLUDE_DIRS}
)

add_executable(bsdtestharness bsdtestharness.c)
add_executable(bsdtestsummarize bsdtestsummarize.c)

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
dispatch_test( dispatch_plusplus )
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
target_include_directories(dispatch_vm PRIVATE ${KQUEUE_INCLUDE_DIRS})
target_link_libraries(dispatch_vm PRIVATE ${KQUEUE_LIBRARIES})

# VNODE dispatch sources are buggy.
dispatch_test( dispatch_vnode )
set_tests_properties(dispatch_vnode PROPERTIES WILL_FAIL TRUE)

# These tests are slow/flaky; don't run them in parallel. FIXME: Investigate
# whether there are actual issues here.
set_tests_properties(
    dispatch_concur
    dispatch_drift
    dispatch_group
    dispatch_io
    dispatch_read2
    dispatch_starfish

    PROPERTIES
        RUN_SERIAL TRUE
        TIMEOUT 100
)
