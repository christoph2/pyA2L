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
#include "spdlog/sinks/stdout_sinks.h"
#include "spdlog/sinks/stdout_color_sinks.h"

class Logger {

public:
    static Logger& get()
    {
        if (!m_instance) {
            m_instance = new Logger();
        }
        return *m_instance;
    }

private:

    Logger() = default;

    ~Logger() {

    }

    Logger(const Logger&) = delete;
    Logger(Logger&&) = delete;

    Logger& operator=(const Logger&) = delete;
    Logger& operator=(Logger&&) = delete;

    static Logger* m_instance;
};


inline auto create_logger(const std::string& name, spdlog::level::level_enum log_level=spdlog::level::warn) -> std::shared_ptr<spdlog::logger> {
    auto logger = spdlog::get(name);
    if (!logger) {
        logger = spdlog::stdout_color_mt(name);
    }
    auto level = logger->level();
    if (level != log_level) {
        logger->set_level(log_level);
    }
    return logger;
}

#if defined(__APPLE__)
    #if defined(EOF)
        #undef EOF
    #endif
#endif

#endif
