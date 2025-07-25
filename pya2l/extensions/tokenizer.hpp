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
#if !defined(__TOKENIZER_HPP)
    #define __TOKENIZER_HPP

    #include <bit>
    #include <sstream>

    #include "ctre.hpp"
    #include "generator.hpp"
    #include "line_numbers.hpp"
    #include "token_type.hpp"
    #include "utils.hpp"

enum class CharClass : int8_t {
    NONE       = -1,
    WHITESPACE = 0,
    REGULAR    = 1,
    STRING     = 1,
};

constexpr char SLASH   = '/';
constexpr char BSLASH  = '\\';
constexpr char ASTERIX = '*';
constexpr char NL      = '\n';
constexpr char CR      = '\r';
constexpr char DQUOTE  = '"';

enum class StringStateType : uint8_t {
    IDLE,
    IN_STRING,
    MAY_CLOSE,
};

enum class CommentStateType : uint8_t {
    IDLE,
    MAY_START,
    SINGLE_LINE,
    OPEN,
    MAY_CLOSE
};

enum class TokenClass : uint8_t {
    REGULAR,
    WHITESPACE,
    COMMENT,
    STRING,
};

/*
** Remove leading and trailing " characters.
*/
static auto trim = [](std::string &str) {
    // NOTE: optimize (std::string_view !?)
    str = str.substr(1, str.length() - 2);
};

class Token {
   public:

    using enum TokenType;

    Token() = default;

    Token(TokenClass token_type, const LineNumbers &line_numbers, const std::string_view &payload) :
        m_token_class{ token_type }, m_line_numbers{ line_numbers }, m_payload{ payload } {
        set_token_type();
    }

    Token &operator=(const Token &) = default;
    Token(const Token &)            = default;
    Token(Token &&)                 = default;

    std::string to_string() noexcept {
        std::stringstream ss;

        ss << "Token(payload='";
        ss << m_payload << "' @";
        ss << m_line_numbers.to_string() << "[" << std::to_string(m_token_type) << "]";
        ss << ")";
        return ss.str();
    }

    TokenClass token_class() const noexcept {
        return m_token_class;
    }

    const std::string &payload() const noexcept {
        return m_payload;
    }

	// Strip leading an tailing characters (usually ").
	std::string stripped_payload() const noexcept {
		return m_payload.substr(1, m_payload.length() - 2);
    }


    const LineNumbers &line_numbers() const noexcept {
        return m_line_numbers;
    }

    uint16_t token_type() const noexcept {
        return m_token_type;
    }

   private:

    static constexpr auto PAT_FLOAT = ctll::fixed_string{ "^[+\\-]?(\\d+([.]\\d*)?([eE][+\\-]?\\d+)?|[.]\\d+([eE][+\\-]?\\d+)?)" };

    static constexpr auto PAT_INT = ctll::fixed_string{ "^(?:[+\\-])?[0-9]+$" };
    static constexpr auto PAT_HEX = ctll::fixed_string{ "^0x[0-9a-fA-F]+$" };

    void set_token_type() noexcept {
        if (m_token_class == TokenClass::WHITESPACE) {
            m_token_type = static_cast<uint16_t>(WS);
        } else if (m_token_class == TokenClass::COMMENT) {
            m_token_type = static_cast<uint16_t>(COMMENT);
        } else if (m_token_class == TokenClass::STRING) {
            m_token_type = static_cast<uint16_t>(STRING);
            // trim(m_payload);
        } else {
            const auto entry = A2L_KEYWORDS.find(m_payload);

            if (entry != A2L_KEYWORDS.end()) {
                m_token_type = static_cast<uint16_t>(entry->second);
            } else {
                if (ctre::match<PAT_INT>(m_payload)) {
                    m_token_type = static_cast<uint16_t>(INT);
                } else if (ctre::match<PAT_HEX>(m_payload)) {
                    m_token_type = static_cast<uint16_t>(HEX);
                } else if (ctre::match<PAT_FLOAT>(m_payload)) {
                    m_token_type = static_cast<uint16_t>(FLOAT);
                } else {
                    // std::cout << "\tIDEN�T: " << m_payload << std::endl;
                    m_token_type = static_cast<uint16_t>(IDENT);
                }
            }
        }
    }

    TokenClass  m_token_class;
    uint16_t    m_token_type{ std::bit_cast<uint16_t>(INVALID) };
    LineNumbers m_line_numbers;
    std::string m_payload;
};

using TokenizerReturnType = Token;

bool                           is_space(char ch);
Generator<TokenizerReturnType> tokenizer(std::basic_istream<char> &stream, bool supress_whitespace = false);

std::vector<Token> split_by_new_line(std::string_view line, std::size_t start_line, std::size_t start_column);

#endif  // __TOKENIZER_HPP
