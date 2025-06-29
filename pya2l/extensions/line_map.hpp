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

    #include <numeric>
    #include <set>

class LineMap {
   public:

    using item_t = std::tuple<std::size_t, std::size_t, std::size_t, std::size_t, std::string>;

    LineMap() noexcept /* : m_line_map()*/ {
    }

    LineMap(const LineMap& other) :
        m_start_offsets(other.m_start_offsets), m_last_line_no(other.m_last_line_no), m_items(other.m_items), m_keys(other.m_keys) {
    }

    LineMap(LineMap&& other) = default;

    // Copy assignment operator
    LineMap& operator=(const LineMap& other) {
        if (this != &other) {
            m_start_offsets = other.m_start_offsets;
            m_last_line_no = other.m_last_line_no;
            m_items = other.m_items;
            m_keys = other.m_keys;
        }
        return *this;
    }

    // Move assignment operator
    LineMap& operator=(LineMap&& other) noexcept {
        if (this != &other) {
            m_start_offsets = std::move(other.m_start_offsets);
            m_last_line_no = other.m_last_line_no;
            m_items = std::move(other.m_items);
            m_keys = std::move(other.m_keys);
        }
        return *this;
    }

    int contains(const std::string& key) const noexcept {
        return m_keys.contains(key);
    }

    std::optional<std::tuple<std::string, std::size_t>> lookup(std::size_t line_no) const noexcept {
        auto item = search_offset(line_no);

        if (item.has_value()) {
            auto idx                                             = item.value();
            auto& [abs_start, abs_end, rel_start, rel_end, name] = m_items[idx];
            int64_t offset                                  = (abs_start - rel_start);
            return std::tuple<std::string, std::size_t>(name, line_no - offset);
        } else {
            return std::nullopt;
        }
    }

    void add_entry(
        const std::string& path, uint64_t abs_start, uint64_t abs_end, uint64_t rel_start, uint64_t rel_end
    ) {
        m_items.push_back(
            std::tuple<decltype(abs_start), decltype(abs_end), decltype(rel_start), decltype(rel_end), decltype(path)>{
                abs_start, abs_end, rel_start, rel_end, path }
        );
        m_start_offsets.push_back(abs_start);
        m_last_line_no = abs_end;
        m_keys.insert(path);
    }

   private:

    std::optional<std::size_t> search_offset(std::size_t key) const noexcept {
        std::size_t left{ 0 };
        std::size_t mid{ 0 };
        std::size_t right{ std::size(m_start_offsets) };

        if (key > m_last_line_no) {
            return std::nullopt;
        }
        while (left < right) {
            mid = std::midpoint(left, right);
            if (key == m_start_offsets[mid]) {
                return mid;
            } else if (key < m_start_offsets[mid]) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }
        return left - 1;
    }

    std::vector<size_t>   m_start_offsets{};
    std::size_t           m_last_line_no{ 0 };
    std::vector<item_t>   m_items{};
    std::set<std::string> m_keys{};
};

#endif  // __LINE_MAP_HPP
