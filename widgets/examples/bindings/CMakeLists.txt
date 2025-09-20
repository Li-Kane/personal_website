cmake_minimum_required(VERSION 3.15)

find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 REQUIRED)

set(KDWIDGETS_BINDINGS_SRC
  py_module.cc
  bind_widgets.cc
)

pybind11_add_module(kdwidgets ${KDWIDGETS_BINDINGS_SRC})
target_link_libraries(kdwidgets PRIVATE kdWidgets::kdWidgets)
target_include_directories(kdwidgets PRIVATE ${CMAKE_SOURCE_DIR}/include)

install(TARGETS kdwidgets DESTINATION .)