add_library(kdWidgets
    Server.cc
)
add_library(kdWidgets::kdWidgets ALIAS kdWidgets)

set_target_properties(kdWidgets PROPERTIES POSITION_INDEPENDENT_CODE ON)

find_library(USOCKETS_LIBRARY uSockets.a PATHS /usr/local/include REQUIRED)
find_package(ZLIB REQUIRED)

target_include_directories(kdWidgets PUBLIC ${CMAKE_SOURCE_DIR}/include)
target_include_directories(kdWidgets PUBLIC /usr/local/include)

target_link_libraries(kdWidgets ${USOCKETS_LIBRARY})
target_link_libraries(kdWidgets ZLIB::ZLIB)