cmake_minimum_required(VERSION 3.15)
# Enable compile commands. Used by LSPs.
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(Eigen3_DIR /home/karana/pkgs/x86_64-ubuntu24/share/eigen3/cmake)
find_package(Karana REQUIRED)

add_executable(chatroom chatroom.cc)
add_executable(iframe iframe.cc)
add_executable(simulation simulation.cc)
add_executable(widgetList widgetList.cc)
target_link_libraries(chatroom kdWidgets::kdWidgets)
target_link_libraries(iframe kdWidgets::kdWidgets)
target_link_libraries(simulation Karana::kdflex kdWidgets::kdWidgets)
target_link_libraries(widgetList kdWidgets::kdWidgets)