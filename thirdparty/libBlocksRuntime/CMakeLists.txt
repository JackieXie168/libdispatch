cmake_minimum_required(VERSION 2.8.7)
project(BlocksRuntime C)

if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE MinSizeRel)
endif ()

include (CheckCSourceCompiles)
include (CheckCCompilerFlag)
#///////////////////////////////////////////////////////////////////////////////

check_c_source_compiles("
int main() {
  int a=0; long b=0;
  __sync_bool_compare_and_swap(&a, 0, 1);
  __sync_bool_compare_and_swap(&b, 0, 1);
}" HAVE_ATOMIC_BUILTINS)

if (HAVE_ATOMIC_BUILTINS)
    set (HAVE_SYNC_BOOL_COMPARE_AND_SWAP_INT 1)
    set (HAVE_SYNC_BOOL_COMPARE_AND_SWAP_LONG 1)
else ()
    message(FATAL_ERROR "Support for GCC atomic builtins is required")
endif ()

check_c_compiler_flag(-fblocks HAVE_FLAGS_FBLOCKS)

set(CONFIG_EPILOGUE
  "#define BLOCK_EXPORT extern __attribute__((visibility(\"default\"), weak))"
)
configure_file(config.h.cmake.in "${CMAKE_CURRENT_BINARY_DIR}/config.h")
#///////////////////////////////////////////////////////////////////////////////

add_definitions(
  -Wall
  -Wextra
  -Wno-unused-parameter
  -Wno-unused-variable
  -Wno-unused-function
  -fvisibility=hidden
  -fPIC
)

include_directories(
    "${CMAKE_CURRENT_SOURCE_DIR}"
    "${CMAKE_CURRENT_BINARY_DIR}")

set(headers
    Block.h
    Block_private.h)

set(sources
    runtime.c
    data.c
    config.h
    ${headers})

add_library(blocksRuntimeStatic STATIC ${sources})
add_library(blocksRuntimeShared SHARED ${sources})

set_target_properties(blocksRuntimeStatic blocksRuntimeShared
    PROPERTIES OUTPUT_NAME BlocksRuntime)

set_target_properties(blocksRuntimeShared PROPERTIES 
    VERSION 0.4.2
    SOVERSION 0
)

if (HAVE_FLAGS_FBLOCKS)
    add_executable(blocksrt-test test/main.c)
    target_link_libraries(blocksrt-test blocksRuntimeShared)
    set_target_properties(blocksrt-test PROPERTIES COMPILE_FLAGS -fblocks)
endif ()

install(TARGETS blocksRuntimeStatic blocksRuntimeShared
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib)
install(FILES ${headers} DESTINATION include/Blocks)
