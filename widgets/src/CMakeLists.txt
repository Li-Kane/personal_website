add_library(kdWidgets
    Server.cc
)
add_library(kdWidgets::kdWidgets ALIAS kdWidgets)

find_package(nlohmann_json 3.2.0 REQUIRED)
find_library(USOCKETS_LIBRARY uSockets.a PATHS /usr/local/include REQUIRED)
find_package(ZLIB REQUIRED)

target_include_directories(kdWidgets PUBLIC ${CMAKE_SOURCE_DIR}/include)
target_include_directories(kdWidgets PUBLIC /usr/local/include)

target_link_libraries(kdWidgets ${USOCKETS_LIBRARY})
target_link_libraries(kdWidgets ZLIB::ZLIB)
target_link_libraries(kdWidgets nlohmann_json::nlohmann_json)