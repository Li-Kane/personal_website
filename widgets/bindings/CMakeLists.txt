set(PYBIND11_FINDPYTHON ON)
# find_package(pybind11 CONFIG REQUIRED)
add_subdirectory(pybind11 EXCLUDE_FROM_ALL)

pybind11_add_module(kdwidgets MODULE
    bindings.cc
    bindwidgets.cc
)

target_include_directories(kdwidgets PRIVATE ${CMAKE_SOURCE_DIR}/include)

install(TARGETS kdwidgets DESTINATION .)