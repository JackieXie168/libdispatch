
set (public_headers
    object.h
)

install(FILES ${public_headers}
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/os")
