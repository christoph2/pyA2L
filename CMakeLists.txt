
cmake_minimum_required(VERSION 3.7...3.18)
project(cmake_example)

find_package(Python COMPONENTS Interpreter Development)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/antlr_cmake)
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/pybind11)
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/pybind11)
message("modules: " ${CMAKE_MODULE_PATH})
# find_package(pybind11 CONFIG REQUIRED PATHS ${CMAKE_CURRENT_SOURCE_DIR}/pybind11)
message( STATUS "Found pybind11 v${pybind11_VERSION} ${pybind11_VERSION_TYPE}: ${pybind11_INCLUDE_DIRS}")
set(ANTLR4_TAG 4.13.1)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/dist")
# set(pybind11_DIR $CACHE{pybind11_DIR})
# set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ../extensions)

# required if linking to static library
add_definitions(-DANTLR4CPP_STATIC)

# using /MD flag for antlr4_runtime (for Visual C++ compilers only)
set(ANTLR4_WITH_STATIC_CRT OFF)

# add external build for antlrcpp
include(ExternalAntlr4Cpp)

# add antrl4cpp artifacts to project environment
include_directories(${ANTLR4_INCLUDE_DIRS})

# set variable pointing to the antlr tool that supports C++
# this is not required if the jar file can be found under PATH environment
set(ANTLR_EXECUTABLE ${CMAKE_CURRENT_SOURCE_DIR}/antlr-${ANTLR4_TAG}-complete.jar)
# add macros to generate ANTLR Cpp code from grammar
find_package(ANTLR REQUIRED)

# Call macro to add lexer and grammar to your build dependencies.
antlr_target(pyA2LLexer ./pya2l/a2llg.g4 LEXER PACKAGE antlrcpptest)

antlr_target(AMLParser ./pya2l/aml.g4 LEXER PARSER LISTENER
              PACKAGE antlrcpptest
              # DEPENDS_ANTLR pyA2LLexer
              # COMPILE_FLAGS -lib ${ANTLR_AMLParser_OUTPUT_DIR}
			  )

# include generated files in project environment
include_directories(${ANTLR_pyA2LLexer_OUTPUT_DIR})
include_directories(${ANTLR_AMLParser_OUTPUT_DIR})

# add generated grammar to demo binary target
# add_executable(demo SHARED a2llg_lexer.cpp ${ANTLR_pyA2LLexer_CXX_OUTPUTS})
# add_executable(schmemo SAHRED aml_parser.cpp ${ANTLR_AMLParser_CXX_OUTPUTS})
# target_link_libraries(demo antlr4_static)
# target_link_libraries(schmemo antlr4_static)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/pya2l/extensions)

pybind11_add_module(preprocessor pya2l/preprocessor_wrapper.cpp pya2l/extensions/tokenizer.cpp)
pybind11_add_module(a2lparser_ext pya2l/a2lparser_wrapper.cpp pya2l/extensions/exceptions.cpp)
# target_include_directories(preprocessor PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/pya2l/extensions>)
# target_link_libraries(preprocessor pybind11::headers)
# set_target_properties(preprocessor PROPERTIES INTERPROCEDURAL_OPTIMIZATION ON CXX_VISIBILITY_PRESET ON VISIBILITY_INLINES_HIDDEN ON)
install(TARGETS preprocessor LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist)
install(TARGETS a2lparser_ext LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist)
