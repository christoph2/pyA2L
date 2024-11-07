#if !defined(__LOGGER_HPP)
#define __LOGGER_HPP

#include <cstdint>
#include <sstream>
#include <iostream>

enum class LogLevel: std::uint8_t {
    DEBUG=10,
    INFO=20,
    WARNING=30,
    ERROR=40,
    CRITICAL=50,
};

inline constexpr std::string loglevel_to_string(LogLevel level) {
    if (level == LogLevel::DEBUG) {
        return "DEBUG";
    } else if  (level == LogLevel::INFO) {
        return "INFO";
    } else if  (level == LogLevel::WARNING) {
        return "WARNING";
    } else if  (level == LogLevel::ERROR) {
        return "ERROR";
    } else if  (level == LogLevel::CRITICAL) {
        return "CRITICAL";
    }
}

class Logger {
public:

    Logger(const std::string& name="", LogLevel level=LogLevel::INFO) : m_name(name), m_level(level) {
    }

    Logger(const Logger& other) {
        m_name = other.m_name;
        m_level = other.m_level;
    }

    Logger(Logger&& other) {
        m_name = other.m_name;
        m_level = std::move(other.m_level);
    }

    Logger& operator=(const Logger & other) {
        m_name = other.m_name;
        m_level = other.m_level;
    }

    Logger& operator=(Logger&& other) {
        m_name = other.m_name;
        m_level = std::move(other.m_level);
    }

    void setLevel(LogLevel level) noexcept {
        m_level = level;
    }

    void setName(const std::string& name) {
        m_name = name;
    }

    template<typename ...Args>
    constexpr void log(LogLevel level, Args&&... args) noexcept {
        std::cout << "[" << loglevel_to_string(level)  << " (" << m_name << ")] ";
        ((std::cout << std::forward<Args>(args) << " "), ...);
        std::cout << std::endl;
    }

    template<typename ...Args>
    constexpr void debug(Args&&... args) noexcept {
        if (LogLevel::DEBUG > m_level) {
            log(LogLevel::DEBUG, args ...);
        }
    }

    template<typename ...Args>
    constexpr void info(Args&&... args) noexcept {
        if (LogLevel::INFO > m_level) {
            log(LogLevel::INFO, args ...);
        }
    }

    template<typename ...Args>
    constexpr void warn(Args&&... args) noexcept {
        if (LogLevel::WARNING > m_level) {
            log(LogLevel::WARNING, args ...);
        }
    }

    template<typename ...Args>
    constexpr void error(Args&&... args) noexcept {
        if (LogLevel::ERROR > m_level) {
            log(LogLevel::ERROR, args ...);
        }
    }

    template<typename ...Args>
    constexpr void critical(Args&&... args) noexcept {
        if (LogLevel::CRITICAL > m_level) {
            log(LogLevel::CRITICAL, args ...);
        }
    }


private:
    std::string m_name;
    LogLevel m_level;
};

extern Logger logger;

#endif // __LOGGER_HPP
