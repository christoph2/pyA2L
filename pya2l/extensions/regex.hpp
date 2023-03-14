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

#if !(__REG_EX_HPP)
#define __REG_EX_HPP

class RegExp {
public:

    RegExp(const std::regex& pattern) : m_pattern(pattern), m_match{} {
    }

    bool operator()(const std::string& text) {
        m_matched = std::regex_search(text, m_match, m_pattern);
        return m_matched;
    }

    int pos(int idx) const {
        return m_match.position(idx);
    }

    int start(int idx) const {
        return pos(idx);
    }

    int end(int idx) const {
        return m_match.position(idx) + m_match.length(idx);
    }

    std::tuple<int, int> span(int idx) const {
        return std::make_tuple(start(idx), end(idx));
    }

    auto str(int idx) const {
        return m_match.str(idx);
    }

    auto prefix() const {
        return m_match.prefix().str();
    }

    auto suffix() const {
        return m_match.suffix().str();
    }

private:
    std::regex m_pattern;
    std::smatch m_match;
    bool m_matched{ false };
};

#endif // __REG_EX_HPP
