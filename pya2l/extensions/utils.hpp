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

enum class State : std::uint8_t {
    IDLE,
    IN_STRING,
};

/*
 * Replace pesky A2L string ""escapes"" by the usual C/C++ \" version.
 */
void escape_string(std::string& line) noexcept {
    State state{ State::IDLE };
    std::size_t pos = line.find('"', 0);
    const std::size_t length = std::size(line);

    if (length == 0 || std::string::npos == pos) {
        return; // Nothing to do.
    }
    state = State::IN_STRING;
    pos += 1;
    while (true) {
        pos = line.find('"', pos);
        switch (state) {
        case State::IDLE:
            if (std::string::npos == pos) {
                return; // We're done.
            }
            else {
                state = State::IN_STRING;
            }
            break;
        case State::IN_STRING:
            if (std::string::npos == pos) {
                // unterminated string -- don't handle, i.e. hand-over to ANTLR.
                return;
            }
            if (pos == length - 1) {
                return; // Line completly processed.
            }
            if (line[pos + 1] == '"' && line[pos - 1] != '\x5c') {
                line[pos] = '\x5c';
                state = State::IN_STRING;
                pos += 2;
            }
            else {
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
static inline void rstrip(std::string& s) noexcept {
    s.erase(std::find_if(s.rbegin(), s.rend(), [](unsigned char ch) {
        return !std::isspace(ch);
        }).base(), s.end());
}

/*
 * Cut out section of text and replace it with a single space.
 */
void blank_out(std::string& text, std::int32_t start, std::int32_t end) noexcept
{
    if (end == -1) {
        text.resize(start);
    }
    else {
        text.erase(text.begin() + start, text.begin() + end);
    }
    rstrip(text);
}

#endif // __UTILS_HPP