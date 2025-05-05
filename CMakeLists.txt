cmake_minimum_required(VERSION 3.10)

project(VCAGame CXX)

set(GODOT_CPP_PATH "C:/Users/Avi/Desktop/VCAGame/godot-cpp")

set(GODOT_CPP_BINARIES "${GODOT_CPP_PATH}/bin")

include_directories("${CMAKE_SOURCE_DIR}/native")

file(GLOB_RECURSE SOURCES
    "${CMAKE_SOURCE_DIR}/native/*.cpp"
    "${CMAKE_SOURCE_DIR}/native/*.h"
)

add_subdirectory(${GODOT_CPP_PATH})

add_library(godot_vc_game SHARED ${SOURCES})

target_link_libraries(godot_vc_game godot-cpp)

set_target_properties(godot_vc_game PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

include_directories("${GODOT_CPP_PATH}/include")

target_include_directories(godot_vc_game PRIVATE "${GODOT_CPP_PATH}/include")
