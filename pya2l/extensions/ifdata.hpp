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

#if !defined(__IFDATA_HPP)
#define __IFDATA_HPP

#include "line_numbers.hpp"

struct IfDataBase {
    using line_type = std::tuple<std::size_t, std::size_t, std::size_t, std::size_t>;
    using map_type = std::map<line_type, std::size_t>;
    const std::size_t HEADER_SIZE = sizeof(std::size_t) * (4 + 1);
};

class IfDataBuilder : public IfDataBase {
public:

    IfDataBuilder(std::ofstream& out) noexcept : m_out(out) {}

    ~IfDataBuilder() {

    }

    void set_line_numbers(std::tuple< std::size_t, std::size_t> start, std::tuple< std::size_t, std::size_t> end) noexcept
    {
        m_line_numbers = LineNumbers(start, end);
    }

    void add_section(std::string& text) noexcept {
        m_length += text.length();
        m_sections.emplace_back(text);
    }

    void add_section(std::string&& text) noexcept {
        m_length += text.length();
        m_sections.emplace_back(std::move(text));
    }


    void finalize() noexcept {
        write_int(m_length);

        // NOTE: line information is NOT required -- only used for testing.
        write_int(m_line_numbers.start_line);
        write_int(m_line_numbers.start_col);
        write_int(m_line_numbers.end_line);
        write_int(m_line_numbers.end_col);

        std::for_each(m_sections.begin(), m_sections.end(), [this](const auto& elem)
            {
                write_string(elem);
            }
        );

        file_map[std::tuple<std::size_t, std::size_t, std::size_t, std::size_t>(m_line_numbers.start_line, m_line_numbers.start_col, m_line_numbers.end_line, m_line_numbers.end_col)] = m_offset;

        m_offset += (HEADER_SIZE + m_length);
        assert(m_out.tellp() == m_offset);

        m_sections.clear();
        m_length = 0;
    }

    map_type& get_map() {
        return file_map;
    }

private:

    void write_int(std::size_t value) {
        m_out.write(reinterpret_cast<char*>(&value), sizeof value);
    }

    void write_string(const std::string& text) {
        m_out << text;
    }

    std::ofstream& m_out;
    LineNumbers m_line_numbers{};
    std::vector<std::string> m_sections{};
    std::size_t m_length{ 0 };
    std::size_t m_offset{ 0 };
    map_type file_map{};
};


class IfDataReader : public IfDataBase {
public:
    IfDataReader() = delete;
    IfDataReader(const std::string& fname, IfDataBuilder& builder) : m_file(fname, /*std::ios::in |*/ std::ios::binary),
        file_map(std::move(builder.get_map())) {}

    ~IfDataReader() {
        m_file.close();
    }

    std::optional<std::string> get(const line_type& line) {

        if (!file_map.contains(line)) {
            return std::nullopt;
        }

        auto offset = file_map[line];

        m_file.seekg(offset);

        auto length = read_int();
        auto start_line = read_int();
        assert(std::get<0>(line) == start_line);
        auto start_col = read_int();
        assert(std::get<1>(line) == start_col);
        auto end_line = read_int();
        assert(std::get<2>(line) == end_line);
        auto end_col = read_int();
        assert(std::get<3>(line) == end_col);
        auto ifdata = read_string(length);

        return ifdata;
    }

private:

    std::size_t read_int() {
        std::size_t value = 0;

        if (!m_file.read(reinterpret_cast<char*>(&value), sizeof value)) {
        }
        return value;
    }

    std::string read_string(std::size_t count) {
        char* value = new char[count + 1];

        m_file.read(value, count);
        value[count] = '\x00';
        std::string result{ value };
        delete[] value;
        return result;
    }

    std::ifstream m_file;
    map_type file_map;
};


#endif // __IFDATA_HPP
