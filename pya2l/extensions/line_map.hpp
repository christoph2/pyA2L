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

#if !defined(__LINE_MAP_HPP)
#define __LINE_MAP_HPP

class LineMap {
public:

    using line_map_item_t = std::tuple<int, int>;
    using line_map_t = std::map<std::string, std::vector<line_map_item_t>>;

    LineMap() : m_line_map() {
    }

    int contains(const std::string& key) const {
        return m_line_map.contains(key);
    }

    std::vector<line_map_item_t>& operator[](const std::string& key) {
        return m_line_map[key];
    }

    std::optional<std::tuple<std::string, std::size_t>> lookup(std::size_t line_no) {
        auto idx = search_offset(line_no);

        if (idx.has_value()) {

            auto [abs_start, abs_end, rel_start, rel_end, name] = items[idx.value()];
            std::int32_t offset = (abs_start - rel_start) - 1;
            std::cout << "\tline_no: " << line_no /* - offset */ << " offset: " << offset << " name: " << name << " abs_start: " << abs_start << " rel_start: " << rel_start << '\n';
            return std::tuple<std::string, std::size_t>(name, line_no - offset);
        }
        else {
            std::cout << "line_no: " << line_no << " not found\n";
            return std::nullopt;
        }

    }

    void finalize() {
        std::size_t  offset{ 0 };
        std::vector<std::tuple<std::size_t, std::size_t, std::string>> sections;
        std::map<std::string, std::size_t> offsets;

        for (const auto& [k, v] : m_line_map) {
            offsets[k] = 1;

        }
        for (const auto& [k, v] : m_line_map) {
            for (const auto& [start, end] : v) {
                sections.push_back(std::make_tuple(start, end, k));
            }
        }
        std::sort(sections.begin(), sections.end(), [](auto& lhs, auto& rhs) {
            return std::get<0>(lhs) < std::get<0>(rhs);
            });

        std::size_t length{ 0 };
        for (auto [start, end, name] : sections) {
            length = end - start;
            start_offsets.push_back(start);
            offset = offsets[name];
            offsets[name] = length + offset;
            last_line_no = end;
            items.push_back(std::make_tuple(start, end, offset, length + offset, name));
        }
        //#if 0
        for (auto [abs_start, abs_end, rel_start, rel_end, name] : items) {
            std::cout << "[" << name << "] " << abs_start << " " << abs_end << " " << rel_start << " " << rel_end << " " << std::endl;
        }
        //#endif

    }

private:

    std::optional<std::size_t> search_offset(std::size_t key) const {
        std::size_t left{ 0 }, mid{ 0 }, right{ std::size(start_offsets) };

        if (key > last_line_no) {
            return std::nullopt;
        }
        while (left < right) {
            mid = left + (right - left) / 2;
            if (key == start_offsets[mid]) {
                return mid;
            }
            else if (key < start_offsets[mid]) {
                right = mid;
            }
            else {
                left = mid + 1;
            }
        }
        return left - 1;
    }

    line_map_t m_line_map{};
    std::vector<size_t> start_offsets{};
    std::size_t last_line_no{ 0 };
    std::vector<std::tuple<std::size_t, std::size_t, std::size_t, std::size_t, std::string>> items{};
};

#endif // __LINE_MAP_HPP
