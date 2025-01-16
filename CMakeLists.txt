
cmake_minimum_required(VERSION 3.10...3.29)
project(pya2l_extensions LANGUAGES C CXX)

cmake_policy(SET CMP0135 NEW)
cmake_policy(SET CMP0094 NEW)

find_package(Python3 COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 REQUIRED)


SET(CMAKE_C_STANDARD 17)
# set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED YES)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
message( STATUS "Found pybind11 v${pybind11_VERSION} ${pybind11_VERSION_TYPE}: ${pybind11_INCLUDE_DIRS}")


set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/dist")

SET(GCC_N_CLANG_BASE_OPTIONS "-Wall -Wextra -Wpedantic -Warray-bounds -mtune=native -fexceptions")

SET(MSVC_BASE_OPTIONS "/W3 /permissive- /EHsc /bigobj /Zc:__cplusplus /std:c++latest")



if (CMAKE_BUILD_TYPE STREQUAL "Debug")
	if (MSVC)
		SET(MSVC_BASE_OPTIONS "${MSVC_BASE_OPTIONS} /Od /fsanitize=address /Zi /FAcs")
	else()
		SET(GCC_N_CLANG_BASE_OPTIONS "${GCC_N_CLANG_BASE_OPTIONS} -Og -g3 -ggdb -fno-omit-frame-pointer -fsanitize=address -fsanitize=undefined -fsanitize=bounds")	# -fsanitize=hwaddress
	endif()
else ()
	if (MSVC)
		SET(MSVC_BASE_OPTIONS "${MSVC_BASE_OPTIONS} /Ox")
	else()
		SET(GCC_N_CLANG_BASE_OPTIONS "${GCC_N_CLANG_BASE_OPTIONS} -O3 -fomit-frame-pointer")
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

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/pya2l/extensions ${PROJECT_SOURCE_DIR}/pya2l/aml)

pybind11_add_module(a2lparser_ext ${CMAKE_CURRENT_SOURCE_DIR}/pya2l/a2lparser_wrapper.cpp ${CMAKE_CURRENT_SOURCE_DIR}/pya2l/extensions/exceptions.cpp
	${CMAKE_CURRENT_SOURCE_DIR}/pya2l/extensions/tokenizer.cpp ${CMAKE_CURRENT_SOURCE_DIR}/pya2l/aml/marshal.cpp	${CMAKE_CURRENT_SOURCE_DIR}/pya2l/aml/parser.cpp)

target_compile_options(a2lparser_ext PUBLIC "-DEXTENSION_NAME=a2lparser_ext" PUBLIC $<$<AND:$<COMPILE_LANGUAGE:CXX>,$<CXX_COMPILER_ID:MSVC>>:/utf-8>)

set(LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/pya2l")

IF (CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
	SET(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${GCC_N_CLANG_BASE_OPTIONS} ${GCC_N_CLANG_EXTRA_OPTIONS}")
	target_link_options(a2lparser_ext PUBLIC -flto=auto)
ELSEIF (CMAKE_C_COMPILER_ID MATCHES "MSVC")
	SET(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${MSVC_BASE_OPTIONS} ${MSVC_EXTRA_OPTIONS}")
ENDIF()

install(TARGETS a2lparser_ext LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/pya2l)
