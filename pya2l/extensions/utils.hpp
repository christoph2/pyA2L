/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

    (C) 2023 by Christoph Schueler <cpu12.gems.googlemail.com>

    All Rights Reserved

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

    s. FLOSS-EXCEPTION.txt
*/

#if !defined(__UTILS_HPP)
    #define __UTILS_HPP

    #include <algorithm>
    #include <optional>
    #include <ranges>
    #include <string>
    #include <vector>

    #define PP_UNREFERENCED_PARAMETER(p) ((p) = (p))

enum class State : std::uint8_t {
    IDLE,
    IN_STRING,
};

/*
 * Replace pesky A2L string ""escapes"" by the usual C/C++ \" version.
 */
inline void escape_string(std::string &line) noexcept {
    State             state{ State::IDLE };
    std::size_t       pos    = line.find('"', 0);
    const std::size_t length = std::size(line);

    if (length == 0 || std::string::npos == pos) {
        return;  // Nothing to do.
    }
    state = State::IN_STRING;
    pos += 1;
    while (true) {
        pos = line.find('"', pos);
        switch (state) {
            case State::IDLE:
                if (std::string::npos == pos) {
                    return;  // We're done.
                } else {
                    state = State::IN_STRING;
                }
                break;
            case State::IN_STRING:
                if (std::string::npos == pos) {
                    // unterminated string -- don't handle, i.e. hand-over to ANTLR.
                    return;
                }
                if (pos == length - 1) {
                    return;  // Line completly processed.
                }
                if (line[pos + 1] == '"' && line[pos - 1] != '\x5c') {
                    line[pos] = '\x5c';
                    state     = State::IN_STRING;
                    pos += 2;
                } else {
                    state = State::IDLE;
                    pos += 1;
                }
                break;
        }
    }
}

/*
 * strip `std::string` from end (in place).
 */
static inline void rstrip(std::string &s) noexcept {
    s.erase(std::find_if(s.rbegin(), s.rend(), [](unsigned char ch) { return !std::isspace(ch); }).base(), s.end());
}

/*
 * Cut out section of text and replace it with a single space.
 */
inline void blank_out(std::string &text, std::int32_t start, std::int32_t end) noexcept {
    if (end == -1) {
        text.resize(start);
    } else {
        text.erase(text.begin() + start, text.begin() + end);
    }
    rstrip(text);
}

inline std::string test_escape_string(std::string &line) {
    std::string result;

    escape_string(line);
    std::ranges::copy(line, std::back_inserter(result));

    return result;
}

inline auto to_string = [](auto &&r) -> std::string {
    const auto data = &*r.begin();
    const auto size = static_cast<std::size_t>(std::ranges::distance(r));

    return std::string{ data, size };
};

inline bool is_space(char ch) {
    if ((ch == '\t') || (ch == '\n') || (ch == '\v') || (ch == '\f') || (ch == '\r') || (ch == '\x20')) {
        return true;
    }
    return false;
}

inline auto split(const std::string &str, char delimiter) -> std::vector<std::string> {
    auto range = str | std::ranges::views::split(delimiter) | std::ranges::views::transform(to_string);

    return { std::ranges::begin(range), std::ranges::end(range) };
}

    #if defined(_MSC_VER)
inline std::optional<std::string> get_env_var(const std::string &var) {
    char       *c_ptr;
    std::size_t len;

    ::errno_t err = _dupenv_s(&c_ptr, &len, var.c_str());
    if ((err == -1) || (len == 0)) {
        return std::nullopt;
    }
    std::string result{ c_ptr };

    ::free(c_ptr);
    return result;
}
    #else
inline std::optional<std::string> get_env_var(const std::string &var) {

        #if (defined(__APPLE__) || defined(_WIN32))
    auto res = getenv(var.c_str());
        #else
    auto res = secure_getenv(var.c_str());
        #endif
    if (res == nullptr) {
        return std::nullopt;
    }
    return res;
}
    #endif

inline std::vector<std::string> split_path(std::optional<std::string> pth) {
    using std::operator""sv;
    #if defined(_WIN32)
    constexpr auto DELIM{ ";"sv };
    #else
    constexpr auto DELIM{ ":"sv };
    #endif

    if (!pth) {
        return {};
    }

    std::vector<std::string> result{};

    std::size_t pos = 0;
    std::string token;
    std::string str{ *pth };
    while ((pos = str.find(DELIM)) != std::string::npos) {
        token = str.substr(0, pos);
        result.emplace_back(token);
        str.erase(0, pos + DELIM.length());
    }
    return result;
}

inline void hex_dump(const char *p, std::size_t n) {
    for (std::size_t idx = 0; idx < n; ++idx) {
        printf("%02X ", p[idx]);
    }
    printf("\n");
}

template<typename T, typename V>
T variant_get(V&& value) {

    T result;

    const T* value_ptr = std::get_if<T>(&value);
    if (value_ptr == nullptr) {
        result = T{};
    }
    else {
        result = *value_ptr;
    }

    return result;
}

#endif  // __UTILS_HPP
