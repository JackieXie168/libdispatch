
set (man_pages
    dispatch.3
    dispatch_after.3
    dispatch_api.3
    dispatch_apply.3
    dispatch_async.3
    dispatch_data_create.3
    dispatch_group_create.3
    dispatch_io_create.3
    dispatch_io_read.3
    dispatch_object.3
    dispatch_once.3
    dispatch_queue_create.3
    dispatch_read.3
    dispatch_semaphore_create.3
    dispatch_source_create.3
    dispatch_time.3
)

configure_file(create_man_symlinks.cmake.in create_man_symlinks.cmake @ONLY)

install(FILES ${man_pages} DESTINATION "${DISPATCH_INSTALL_MAN_DIR}")
install(SCRIPT "${CMAKE_CURRENT_BINARY_DIR}/create_man_symlinks.cmake")
