#if !defined(__LOGGER_HPP)
#define __LOGGER_HPP

#if !defined(__APPLE__)
    #define SPDLOG_USE_STD_FORMAT   (1)
#else
    #include <cstdio>
    #if !defined(EOF)
        #define EOF (-1)
    #endif
#endif

#include "spdlog/spdlog.h"

#if defined(__APPLE__)
    #if defined(EOF)
        #undef EOF
    #endif
#endif

#endif
