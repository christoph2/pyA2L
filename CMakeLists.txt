
cmake_minimum_required(VERSION 3.7...3.29)
project(pya2l_extensions LANGUAGES C CXX)

cmake_policy(SET CMP0135 NEW)
cmake_policy(SET CMP0094 NEW)

find_package(Python3 COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)


# set(ANTLR4_TAG 4.13.2)
set(ANTLR4_TAG $ENV{ANTLR4_TAG})

message("ANTLR4-TAG: " ${ANTLR4_TAG})

SET(CMAKE_C_STANDARD 17)
# set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD 20)
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/antlr_cmake)

add_definitions(-DANTLR4CPP_STATIC)
set(ANTLR4_WITH_STATIC_CRT OFF)
include(ExternalAntlr4Cpp)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

include_directories(SYSTEM ${ANTLR4_INCLUDE_DIRS})

set(ANTLR_EXECUTABLE ${CMAKE_CURRENT_SOURCE_DIR}/antlr-tool/antlr-${ANTLR4_TAG}-complete.jar)

if(NOT EXISTS "${ANTLR_EXECUTABLE}")
    message ("ANTLR .jar \"${ANTLR_EXECUTABLE}\" does not exist!")
    message("Downloading "  "https://www.antlr.org/download/antlr-${ANTLR4_TAG}-complete.jar")
    file(DOWNLOAD "https://www.antlr.org/download/antlr-${ANTLR4_TAG}-complete.jar" "${ANTLR_EXECUTABLE}")
endif()

find_package(ANTLR REQUIRED)

message( STATUS "Found pybind11 v${pybind11_VERSION} ${pybind11_VERSION_TYPE}: ${pybind11_INCLUDE_DIRS}")

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/dist")


SET(GCC_N_CLANG_BASE_OPTIONS "-Wall -Wextra -Wpedantic -Warray-bounds -mtune=native -fexceptions")

SET(MSVC_BASE_OPTIONS "/W3 /permissive- /EHsc /bigobj /Zc:__cplusplus /std:c++latest")



if (CMAKE_BUILD_TYPE STREQUAL "Debug")
	if (MSVC)
		SET(MSVC_BASE_OPTIONS "${MSVC_BASE_OPTIONS} /Od /fsanitize=address /Zi /FAcs")
	else()
		SET(MSVC_BASE_OPTIONS "${MSVC_BASE_OPTIONS} -Og -g3 -ggdb --fno-omit-frame-pointer -fsanitize=address -fsanitize=undefined -fsanitize=bounds")	# -fsanitize=hwaddress
	endif()
else ()
	if (MSVC)
		SET(MSVC_BASE_OPTIONS "${MSVC_BASE_OPTIONS} /Ox")
	else()
		SET(MSVC_BASE_OPTIONS "${MSVC_BASE_OPTIONS} -O3 --fomit-frame-pointer")
	endif()
 endif ()


if (CMAKE_SYSTEM_NAME STREQUAL  "Darwin")
    set(ENV{MACOSX_DEPLOYMENT_TARGET}  "11.0")
	SET(GCC_N_CLANG_EXTRA_OPTIONS "-stdlib=libc++")
	message("Platform is Darwin")
elseif (CMAKE_SYSTEM_NAME STREQUAL  "Windows")
	message("Platform is WINDOWS")
	SET(MSVC_EXTRA_OPTIONS "")
elseif (CMAKE_SYSTEM_NAME STREQUAL  "Linux")
    SET(GCC_N_CLANG_EXTRA_OPTIONS "-fvisibility=hidden -g0") # -fcoroutines
	message("Platform is LINUX")
endif()


IF (CMAKE_C_COMPILER_ID STREQUAL "GNU")

ELSEIF (CMAKE_C_COMPILER_ID MATCHES "Clang")

ELSEIF (CMAKE_C_COMPILER_ID MATCHES "MSVC")

ELSE ()

ENDIF ()

IF (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")

ELSEIF (CMAKE_CXX_COMPILER_ID MATCHES "Clang")

ELSEIF (CMAKE_CXX_COMPILER_ID MATCHES "MSVC")

ELSE ()


ENDIF ()

message("Compiling C with: " ${CMAKE_C_COMPILER_ID})
message("Compiling Cpp with: " ${CMAKE_CXX_COMPILER_ID})

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)


# Call macro to add lexer and grammar to your build dependencies.
antlr_target(pyA2LLexer ${CMAKE_CURRENT_SOURCE_DIR}/pya2l/a2llg.g4 LEXER
			# PACKAGE pya2l
			OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/pya2l/aml/
			)

antlr_target(AMLParser ${CMAKE_CURRENT_SOURCE_DIR}/pya2l/aml.g4 LEXER PARSER
              # PACKAGE pya2l
			  VISITOR
			  OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/pya2l/aml/
              DEPENDS_ANTLR pyA2LLexer
              # COMPILE_FLAGS -lib ${ANTLR_AMLParser_OUTPUT_DIR}
			  )

add_executable(aml_tester ${CMAKE_CURRENT_SOURCE_DIR}/pya2l/aml_parser.cpp
	${CMAKE_CURRENT_SOURCE_DIR}/pya2l/aml/aml_visitor.cpp ${CMAKE_CURRENT_SOURCE_DIR}/pya2l/aml/marshal.cpp ${CMAKE_CURRENT_SOURCE_DIR}/pya2l/aml/unmarshal.cpp
	${ANTLR_AMLParser_CXX_OUTPUTS}
)

add_executable(if_data_parser ${CMAKE_CURRENT_SOURCE_DIR}/pya2l/if_data_parser.cpp
	${CMAKE_CURRENT_SOURCE_DIR}/pya2l/aml/unmarshal.cpp
	${ANTLR_AMLParser_CXX_OUTPUTS}
	${ANTLR_pyA2LLexer_CXX_OUTPUTS}
)

target_link_libraries(aml_tester antlr4_static ${SYSTEM_LIBS})
target_link_libraries(if_data_parser antlr4_static ${SYSTEM_LIBS})

# target_include_directories(aml_tester PUBLIC $<BUILD_INTERFACE:${ANTLR4_INCLUDE_DIRS})
 target_include_directories(aml_tester PUBLIC ${ANTLR4_INCLUDE_DIRS} ${ANTLR_AMLParser_OUTPUT_DIR} ${PROJECT_SOURCE_DIR}/pya2l/aml)
 target_include_directories(if_data_parser PUBLIC ${ANTLR4_INCLUDE_DIRS} ${ANTLR_pyA2LLexer_OUTPUT_DIR} ${ANTLR_AMLParser_OUTPUT_DIR} ${PROJECT_SOURCE_DIR}/pya2l/aml)	# !?

message("aml_tester / output: " ${aml_tester_OUTPUT_DIRECTORY})


# include generated files in project environment
include_directories(${ANTLR_pyA2LLexer_OUTPUT_DIR}/pya2l)
include_directories(${ANTLR_AMLParser_OUTPUT_DIR}/pya2l)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/pya2l/extensions)

pybind11_add_module(a2lparser_ext pya2l/a2lparser_wrapper.cpp pya2l/extensions/exceptions.cpp pya2l/extensions/tokenizer.cpp)
pybind11_add_module(amlparser_ext pya2l/amlparser_wrapper.cpp ${CMAKE_CURRENT_SOURCE_DIR}/pya2l/aml/aml_visitor.cpp ${CMAKE_CURRENT_SOURCE_DIR}/pya2l/aml/marshal.cpp
	${CMAKE_CURRENT_SOURCE_DIR}/pya2l/aml/parser.cpp ${ANTLR_AMLParser_CXX_OUTPUTS})

target_link_libraries(amlparser_ext PRIVATE antlr4_static) # ${SYSTEM_LIBS})
target_compile_options(a2lparser_ext PUBLIC "-DEXTENSION_NAME=a2lparser_ext")
target_compile_options(amlparser_ext PUBLIC "-DEXTENSION_NAME=amlparser_ext")

set(LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/pya2l")

IF (CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
	SET(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${GCC_N_CLANG_BASE_OPTIONS} ${GCC_N_CLANG_EXTRA_OPTIONS}")
	target_link_options(a2lparser_ext PUBLIC -flto=auto)
ELSEIF (CMAKE_C_COMPILER_ID MATCHES "MSVC")
	SET(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${MSVC_BASE_OPTIONS} ${MSVC_EXTRA_OPTIONS}")
ENDIF()

install(TARGETS a2lparser_ext LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/pya2l)
install(TARGETS amlparser_ext LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/pya2l)
# install(TARGETS aml_tester LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/pya2l)
# install(TARGETS if_data_parser LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/pya2l)
