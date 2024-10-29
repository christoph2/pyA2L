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

#if !defined(__LINE_NUMBERS_HPP)
    #define __LINE_NUMBERS_HPP

struct LineNumbers {
    LineNumbers() = default;

    LineNumbers(std::size_t sl, std::size_t sc, std::size_t el, std::size_t ec) noexcept :
        start_line(sl), start_col(sc), end_line(el), end_col(ec) {
    }

    LineNumbers(const LineNumbers &) = default;
    LineNumbers(LineNumbers &&) = default;
    LineNumbers& operator=(const LineNumbers &) = default;
    LineNumbers& operator=(LineNumbers &&) = default;

    LineNumbers(std::tuple< std::size_t, std::size_t> start, std::tuple< std::size_t, std::size_t> end) noexcept :
        start_line(std::get<0>(start)), start_col(std::get<1>(start)), end_line(std::get<0>(end)), end_col(std::get<1>(end)) {
    }

    std::tuple<std::size_t, std::size_t, std::size_t, std::size_t> get() const noexcept {
        return std::tuple<std::size_t, std::size_t, std::size_t, std::size_t>(start_line, start_col, end_line, end_col);
    }

    std::string to_string() {
        std::stringstream ss;

        ss << std::to_string(start_line) << ":" << std::to_string(start_col) << ";" << std::to_string(end_line) << ":"
           << std::to_string(end_col);

        return ss.str();
    }

    std::size_t start_line, start_col;
    std::size_t end_line, end_col;
};

#endif  // __LINE_NUMBERS_HPP
