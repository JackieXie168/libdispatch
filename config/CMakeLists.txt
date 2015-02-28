include (../cmake/BuildUtil.cmake)

#-------------------------------------------------------------------------------
# Depends on tests performed in the toplevel CMakeLists.txt
set (USE_LIBDISPATCH_INIT_CONSTRUCTOR ${DISPATCH_USE_LIBDISPATCH_INIT_CONSTRUCTOR})
set (HAVE_PTHREAD_WORKQUEUES ${DISPATCH_ENABLE_PTHREAD_WORKQUEUE})
#-------------------------------------------------------------------------------
dispatch_check_decls(CLOCK_UPTIME CLOCK_MONOTONIC INCLUDES time.h)
dispatch_check_decls(F_RDADVISE INCLUDES fcntl.h)
dispatch_check_decls(FD_COPY INCLUDES sys/select.h)
dispatch_check_decls(POSIX_SPAWN_SETEXEC POSIX_SPAWN_START_SUSPENDED
    INCLUDES sys/spawn.h)
dispatch_check_decls(SIGEMT INCLUDES signal.h)
dispatch_check_decls(TAILQ_FOREACH_SAFE INCLUDES sys/queue.h)
dispatch_check_decls(VQ_UPDATE VQ_VERYLOWDISK INCLUDES sys/mount.h)

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

if (HAVE_UNISTD_H AND DISPATCH_ENABLE_BLOCKS)
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

# Test if __builtin_ffs() takes a signed argument.
check_c_source_compiles("int __builtin_ffs(int); int main(){}"
    HAVE_WORKING_BUILTIN_FFS)
if (NOT HAVE_WORKING_BUILTIN_FFS)
    set( HAVE_PROBLEMATIC_BUILTIN_FFS 1 )
endif ()

set( USE_FUTEX_SEM 1 )

dispatch_add_configure_depends(
    "${CMAKE_CURRENT_SOURCE_DIR}/config.cnf"
    "${CMAKE_CURRENT_SOURCE_DIR}/regen_config.py"
)

execute_process(
    COMMAND ${PYTHON_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/regen_config.py"
            "${CMAKE_CURRENT_SOURCE_DIR}/config.cnf"
            "${CMAKE_CURRENT_BINARY_DIR}/config.h.cmake.in"
)

configure_file("${CMAKE_CURRENT_BINARY_DIR}/config.h.cmake.in" "config.h" @ONLY)
