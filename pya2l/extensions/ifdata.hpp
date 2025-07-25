/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

    (C) 2024 by Christoph Schueler <cpu12.gems.googlemail.com>

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

#if !defined(__IFDATA_HPP)
    #define __IFDATA_HPP

// #define __STDC_WANT_LIB_EXT1__ (1)

    #include <sys/stat.h>

    #include <bit>
    #include <cstdio>

    #include "logger.hpp"
    #include "tokenizer.hpp"

using line_type = std::tuple< std::size_t, std::size_t>;

template<>
struct std::hash<line_type> {
    std::size_t operator()(const line_type& o) const noexcept {
        auto [l, r] = o;
        return std::hash<unsigned long long>{}(l) ^ std::hash<unsigned long long>{}(r);
    }
};

struct IfDataBase {
    using map_type                = std::unordered_map<line_type, std::size_t>;
    const std::size_t HEADER_SIZE = sizeof(std::size_t) * (4 + 1);
};

class IfDataBuilder : public IfDataBase {
   public:

    // Constructor
    IfDataBuilder(std::ofstream& out) noexcept : m_out(out) {
        m_out.seekp(0);
    }

    // Copy constructor - both objects will reference the same stream
    IfDataBuilder(const IfDataBuilder& other) :
        m_out(other.m_out),
        m_line_numbers(other.m_line_numbers),
        m_tokens(other.m_tokens),
        m_length(other.m_length),
        m_offset(other.m_offset),
        file_map(other.file_map) {
    }

    // Delete copy assignment operator - references can't be reseated
    IfDataBuilder& operator=(const IfDataBuilder&) = delete;

    // Move constructor - references can't be reseated, so we just keep our reference
    IfDataBuilder(IfDataBuilder&& other) noexcept :
        m_out(other.m_out),
        m_line_numbers(std::move(other.m_line_numbers)),
        m_tokens(std::move(other.m_tokens)),
        m_length(other.m_length),
        m_offset(other.m_offset),
        file_map(std::move(other.file_map)) {
    }

    // Move assignment operator - references can't be reseated, so we just keep our reference
    IfDataBuilder& operator=(IfDataBuilder&& other) noexcept {
        if (this != &other) {
            // Can't move m_out as it's a reference
            m_line_numbers = std::move(other.m_line_numbers);
            m_tokens       = std::move(other.m_tokens);
            m_length       = other.m_length;
            m_offset       = other.m_offset;
            file_map       = std::move(other.file_map);
        }
        return *this;
    }

    ~IfDataBuilder() {
    }

    void add_token(Token& token) noexcept {m_length += token.payload().length();
        m_tokens.emplace_back(token);
    }

    void finalize() noexcept {
        set_line_numbers();

        write_int(m_length);

        // NOTE: line information is NOT required -- only used for testing.
        write_int(m_line_numbers.start_line);
        write_int(m_line_numbers.start_col);
        write_int(m_line_numbers.end_line);
        write_int(m_line_numbers.end_col);

        for (auto&& elem : m_tokens) {
            write_string(elem.payload());
        }

        file_map[std::tuple<std::size_t, std::size_t>(m_line_numbers.start_line, m_line_numbers.start_col)] = m_offset;

        m_offset += (HEADER_SIZE + m_length);
        // assert(m_out.tellp() == m_offset);
        m_tokens.clear();
        m_length = 0;
    }

    map_type& get_map() {
        return file_map;
    }

   private:

    void set_line_numbers() noexcept {
        uint64_t start_line = 0;
        uint64_t start_col  = 0;

        for (auto tk : m_tokens) {
            if ((tk.token_class() == TokenClass::REGULAR) && (tk.payload() == "IF_DATA")) {
                start_line = tk.line_numbers().start_line;
                start_col  = tk.line_numbers().start_col;
                break;
            }
        }

        // auto start     = m_tokens[0].m_line_numbers;
        auto end       = m_tokens[m_tokens.size() - 1].line_numbers();
        m_line_numbers = LineNumbers(start_line, start_col, end.end_line, end.end_col);
    }

    void write_int(std::size_t value) {
        m_out.write(std::bit_cast<const char*>(&value), sizeof value);
    }

    void write_string(std::string_view text) {
        m_out << text;
    }

    std::ofstream&     m_out;
    LineNumbers        m_line_numbers{};
    std::vector<Token> m_tokens{};
    std::size_t        m_length{ 0 };
    std::size_t        m_offset{ 0 };
    map_type           file_map{};
};

class IfDataReader : public IfDataBase {
   public:

    IfDataReader() = default;

    IfDataReader(const IfDataReader& other) {
        m_file_name = other.m_file_name;
        m_file      = other.m_file;
        file_map    = other.file_map;
    }

    IfDataReader(IfDataReader&& other) noexcept {
        m_file_name = std::move(other.m_file_name);
        m_file      = std::move(other.m_file);
        file_map    = std::move(other.file_map);
    }

    IfDataReader& operator=(const IfDataReader& other) {
        if (this != &other) {
            // Close current file if open
            close();

            // Copy members
            m_file_name = other.m_file_name;
            m_file      = nullptr;  // Don't copy the file pointer, we'll reopen if needed
            file_map    = other.file_map;
            m_size      = other.m_size;
            m_file_open = false;
        }
        return *this;
    }

    IfDataReader& operator=(IfDataReader&& other) noexcept {
        if (this != &other) {
            // Close current file if open
            close();

            // Move members
            m_file_name = std::move(other.m_file_name);
            m_file      = other.m_file;
            file_map    = std::move(other.file_map);
            m_size      = other.m_size;
            m_file_open = other.m_file_open;

            // Reset other's file pointer to prevent double-close
            other.m_file      = nullptr;
            other.m_file_open = false;
        }
        return *this;
    }

    IfDataReader(std::string_view fname, IfDataBuilder& builder) : m_file_name(fname), file_map(std::move(builder.get_map())) {
    }

    void open() {
    #if defined(_MSC_VER)
        auto err = ::fopen_s(&m_file, m_file_name.c_str(), "rb");
        if (err != 0) {
            throw std::runtime_error("Could not open file '" + m_file_name + "'.\n");
        }
    #else
        m_file = ::fopen(m_file_name.c_str(), "rb");
        if (m_file == nullptr) {
            throw std::runtime_error("Could not open file '" + m_file_name + "'.\n");
        }
    #endif

        struct stat stat_buf;
        int         rc = stat(m_file_name.c_str(), &stat_buf);
        m_size         = rc == 0 ? stat_buf.st_size : -1;
        m_file_open    = true;
    }

    void close() {
        if (m_file_open) {
            ::fclose(m_file);
            m_file_open = false;
        }
    }

    ~IfDataReader() {
        close();
    }

    std::optional<std::string> get(const line_type& line) {
        if (!file_map.contains(line)) {
            return std::nullopt;
        }
        auto offset = static_cast<long>(file_map[line]);

        if (m_file == nullptr) {
            open();
        }

        if (offset >= m_size) {
            spdlog::get("a2lparser")->error("file offset {} is out of range of file size {}", offset, m_size);
            return std::nullopt;
        }

        ::fseek(m_file, offset, SEEK_SET);
        auto length = read_int();
        // #if (defined(CMAKE_BUILD_TYPE)) && (CMAKE_BUILD_TYPE == Debug)
        auto start_line = read_int();
        // assert(std::get<0>(line) == start_line);
        auto start_col = read_int();
        // assert(std::get<1>(line) == start_col);
        auto end_line = read_int();
        // assert(std::get<2>(line) == end_line);
        auto end_col = read_int();
        // assert(std::get<3>(line) == end_col);
        // #endif
        auto ifdata = read_string(length);
        return ifdata;
    }

   private:

    std::size_t read_int() {
        std::size_t value = 0;

        ::fread((char*)&value, sizeof(std::size_t), 1, m_file);
        return value;
    }

    std::string read_string(std::size_t count) {
        std::vector<char> buf(count + 1);

        ::fread(buf.data(), 1, count, m_file);
        buf[count] = '\x00';
        std::string result{ buf.data() };
        return result;
    }

    std::string m_file_name;
    std::FILE*  m_file{ nullptr };
    map_type    file_map;
    std::size_t m_size{ 0 };
    bool        m_file_open{ false };
};

#endif  // __IFDATA_HPP
