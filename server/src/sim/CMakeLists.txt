cmake_minimum_required(VERSION 3.8)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
project(sim)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sim_interfaces REQUIRED)
find_package(ament_index_cpp REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# for kdFlex
set(Eigen3_DIR /usr/share/eigen3/cmake)
find_package(Boost REQUIRED COMPONENTS thread filesystem atomic serialization chrono)
find_package(OpenSSL 3 REQUIRED)
find_package(Karana REQUIRED)

# Build spot_env as a library
add_library(spot_env src/spot_env.cpp)
target_link_libraries(spot_env Karana::kdflex)
target_include_directories(spot_env PUBLIC include)
ament_target_dependencies(spot_env ament_index_cpp)

# Build sim_node executable
add_executable(sim_node src/sim_node.cpp)
target_link_libraries(sim_node spot_env)
ament_target_dependencies(sim_node rclcpp sim_interfaces)

install(TARGETS
  sim_node
  DESTINATION lib/${PROJECT_NAME}
)

# Install assets directory
install(DIRECTORY
  assets/
  DESTINATION share/${PROJECT_NAME}/assets
)

ament_package()
