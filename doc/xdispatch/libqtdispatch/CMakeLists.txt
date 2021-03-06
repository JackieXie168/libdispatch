
file(GLOB QSRC *.h *.cpp)
file(GLOB QHEADER *.h)
file(GLOB QINCLUDE_H
    ../include/QtDispatch/*.h
    ../include/QtDispatch/QBlockRunnable
    ../include/QtDispatch/QDispatch
    ../include/QtDispatch/QDispatchApplication
    ../include/QtDispatch/QDispatchCoreApplication
    ../include/QtDispatch/QDispatchGroup
    ../include/QtDispatch/QDispatchQueue
    ../include/QtDispatch/QDispatchSemaphore
    ../include/QtDispatch/QDispatchSource
    ../include/QtDispatch/QDispatchTimer
    ../include/QtDispatch/QIterationBlockRunnable
    ../include/QtDispatch/QIterationRunnable
    ../include/QtDispatch/QtDispatch
)
file(GLOB QINCLUDE ../include/QtDispatch/Q*)

# include qt headers (if found)	
INCLUDE_DIRECTORIES(
	${QT_QTCORE_INCLUDE_DIR}
        ${CMAKE_CURRENT_BINARY_DIR}
)

# tell qt we're building a dll
mz_add_definition(QT_MAKEDLL)

# assume an installation
include_directories(
    ../include
)

# moc qt files
mz_auto_moc(MOC ${QHEADER} ${QINCLUDE_H})
qt4_generate_moc(qdispatchgroup.cpp ${CMAKE_CURRENT_BINARY_DIR}/moc_qdispatchgroup.moc)

source_group(src FILES ${QSRC} ${QHEADER})
source_group(includes FILES ${QINCLUDE} ${QINCLUDE_H})

# res file
if(WIN32)
	set(RES_FILE ${CMAKE_CURRENT_BINARY_DIR}/version.rc)
	configure_file(${CMAKE_CURRENT_SOURCE_DIR}/version.rc.in ${CMAKE_CURRENT_BINARY_DIR}/version.rc)
endif()

if( IOS )
	set( QTDISPATCH_BUILD_TYPE STATIC )
else()
	set( QTDISPATCH_BUILD_TYPE SHARED )
endif()

add_library(QtDispatch ${QTDISPATCH_BUILD_TYPE} ${QSRC} ${MOC} ${QHEADER} ${QINCLUDE} ${QINCLUDE_H} ${CMAKE_CURRENT_BINARY_DIR}/moc_qdispatchgroup.moc ${RES_FILE})
target_link_libraries(QtDispatch xdispatch ${QT_QTCORE_LIBRARY} ${QT_QTGUI_LIBRARY})

mz_target_props(QtDispatch)
set_property(TARGET QtDispatch PROPERTY VERSION ${XDISPATCH_VERSION})
set_property(TARGET QtDispatch PROPERTY SOVERSION ${XDISPATCH_VERSION})

if(IOS)
    install(TARGETS QtDispatch
                LIBRARY DESTINATION lib
                RUNTIME DESTINATION bin
                ARCHIVE DESTINATION lib)
    install(DIRECTORY ../include/QtDispatch
                DESTINATION include
                PATTERN "*.svn" EXCLUDE)
                
elseif(APPLE)
    set_property(TARGET QtDispatch PROPERTY FRAMEWORK TRUE)
    set_property(TARGET QtDispatch PROPERTY PUBLIC_HEADER ${QINCLUDE_H})

    install(TARGETS QtDispatch
                COMPONENT libQtDispatch
                FRAMEWORK DESTINATION "Library/Frameworks")
else()
    install(TARGETS QtDispatch
                COMPONENT libQtDispatch
                LIBRARY DESTINATION lib
                RUNTIME DESTINATION bin
                ARCHIVE DESTINATION lib)
    install(DIRECTORY ../include/QtDispatch
                DESTINATION include
                COMPONENT libQtDispatch-dev
                PATTERN "*.svn" EXCLUDE)
endif()
