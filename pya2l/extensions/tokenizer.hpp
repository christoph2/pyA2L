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
#if !defined(__tokenizer_hpp)
    #define __tokenizer_hpp

    #include "generator.hpp"
    #include "line_numbers.hpp"
    #include "token_type.hpp"
    #include "utils.hpp"

enum class CharClass : std::int8_t {
    NONE       = -1,
    WHITESPACE = 0,
    REGULAR    = 1,
    STRING     = 1,
};

const char SLASH   = '/';
const char ASTERIX = '*';
const char NL      = '\n';
const char CR      = '\r';
const char DQUOTE  = '"';

enum class StringStateType : std::uint8_t {
    IDLE,
    IN_STRING,
    MAY_CLOSE,
};

enum class CommentStateType : std::uint8_t {
    IDLE,
    MAY_START,
    SINGLE_LINE,
    OPEN,
    MAY_CLOSE
};

enum class TokenClass : std::uint8_t {
    REGULAR,
    WHITESPACE,
    COMMENT,
};

struct Token {
    Token() = default;

    Token(TokenClass token_type, const LineNumbers& line_numbers, std::string_view payload) :
        m_token_class{ token_type }, m_line_numbers{ line_numbers }, m_payload{ payload } {
    }

    TokenClass  m_token_class;
    LineNumbers m_line_numbers;
    std::string m_payload;
};

using TokenizerReturnType = Token;

bool                           is_space(char ch);
Generator<TokenizerReturnType> tokenizer(std::basic_istream<char>& stream, bool supress_whitespace = false);

std::vector<Token> split_by_new_line(std::string_view line, std::size_t start_line, std::size_t start_column);

#endif  // __tokenizer_hpp
