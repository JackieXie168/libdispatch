include(CheckIncludeFile)
include(CheckSymbolExists)
include(CheckFunctionExists)

check_include_file("err.h" "HAVE_ERR_H")
check_include_file("sys/eventfd.h" "HAVE_SYS_EVENTFD_H")
check_include_file("sys/signalfd.h" "HAVE_SYS_SIGNALFD_H")
check_include_file("sys/timerfd.h" "HAVE_SYS_TIMERFD_H")

check_symbol_exists("EPOLLRDHUP" "sys/epoll.h" "HAVE_DECL_EPOLLRDHUP")
check_symbol_exists("PORT_SOURCE_FILE" "sys/port.h" "HAVE_DECL_PORT_SOURCE_FILE")

check_function_exists("ppoll" "HAVE_PPOLL")
