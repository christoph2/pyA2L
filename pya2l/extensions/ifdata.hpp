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

    IfDataBuilder(std::ofstream& out) noexcept : m_out(out) {
        m_out.seekp(0);
    }

    ~IfDataBuilder() {
    }

    void add_token(const Token& token) noexcept {
        m_length += token.m_payload.length();
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
            write_string(elem.m_payload);
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
        std::uint64_t start_line = 0;
        std::uint64_t start_col  = 0;

        for (auto tk : m_tokens) {
            if ((tk.m_token_class == TokenClass::REGULAR) && (tk.m_payload == "IF_DATA")) {
                start_line = tk.m_line_numbers.start_line;
                start_col  = tk.m_line_numbers.start_col;
                break;
            }
        }

        // auto start     = m_tokens[0].m_line_numbers;
        auto end       = m_tokens[m_tokens.size() - 1].m_line_numbers;
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

    IfDataReader& operator=(const IfDataReader&) = delete;

    IfDataReader& operator=(IfDataReader&&) = delete;

    IfDataReader(std::string_view fname, IfDataBuilder& builder) : m_file_name(fname), file_map(std::move(builder.get_map())) {
    }

    void open() {
    #if defined(_MSC_VER)
        auto err = ::fopen_s(&m_file, m_file_name.c_str(), "rb");
    #else
        m_file = ::fopen(m_file_name.c_str(), "rb");
    #endif

        struct stat stat_buf;
        int         rc = stat(m_file_name.c_str(), &stat_buf);
        m_size         = rc == 0 ? stat_buf.st_size : -1;
    }

    void close() {
        ::fclose(m_file);
    }

    ~IfDataReader() {
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
            std::cerr << "file offset " << offset << " is out of range of file size " << m_size << std::endl;
            return std::nullopt;
        } else {
            // std::cout << "file offset: " << offset << std::endl;
        }

        ::fseek(m_file, offset, SEEK_SET);
        // std::cout << "\t\tOK\n";

        auto length     = read_int();
        auto start_line = read_int();
        // assert(std::get<0>(line) == start_line);
        auto start_col = read_int();
        // assert(std::get<1>(line) == start_col);
        auto end_line = read_int();
        // assert(std::get<2>(line) == end_line);
        auto end_col = read_int();
        // assert(std::get<3>(line) == end_col);
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
};

#endif  // __IFDATA_HPP
