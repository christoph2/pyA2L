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

#include "tokenizer.hpp"


auto split_single_line_comment(const std::string& line, std::size_t start_line, std::size_t start_column) {
    std::string::size_type pos = line.find("//");
    std::vector<Token> result;

    if (pos > 0) {
        LineNumbers line_numbers{ start_line, start_column, start_line, start_column + pos - 1 };
        result.push_back(Token{ TokenType::REGULAR, line_numbers, line.substr(0, pos) });
        line_numbers = { start_line, start_column + pos, start_line, line.length() - pos };
        result.push_back(Token{ TokenType::COMMENT, line_numbers, line.substr(pos, line.length() - pos - 1) });
        line_numbers = { start_line, line.length() - pos + 1, start_line, line.length() - pos + 1 };
        result.push_back(Token{ TokenType::WHITESPACE, line_numbers, "\n" });
    }
    else {
        LineNumbers line_numbers{ start_line, start_column, start_line, line.length() - 1 };
        result.push_back(Token{ TokenType::COMMENT, line_numbers, line.substr(0, line.length() - 1) });
        line_numbers = { start_line, line.length(), start_line, line.length() };
        result.push_back(Token{ TokenType::WHITESPACE, line_numbers, "\n" });
    }
    return result;
}

auto split_multi_line_comment(const std::string& line, std::size_t start_line, std::size_t start_column, std::size_t end_line, std::size_t end_column) {
    std::string::size_type start_pos = line.find("/*");
    std::string::size_type end_pos = line.find("*/");
    auto len = line.length();
    std::vector<Token> result;

    if (start_pos > 0) {
        LineNumbers line_numbers{ start_line, start_column, start_line, start_column + start_pos - 1 };
        result.push_back(Token{ TokenType::REGULAR, line_numbers, line.substr(0, start_pos) });
        line_numbers = { start_line, start_column + start_pos, start_line, line.length() };
        result.push_back(Token{ TokenType::COMMENT, line_numbers, line.substr(start_pos, line.length() - start_pos) });
    }
    else {
        LineNumbers line_numbers = { start_line, start_column + start_pos, end_line, end_column + 1 };
        result.push_back(Token{ TokenType::COMMENT, line_numbers, line });
    }

    return result;
}

Generator <TokenizerReturnType> tokenizer(std::basic_istream<char>& stream, bool supress_whitespace) {
    char ch{};
    char previous_ch{};
    StringStateType string_state{ StringStateType::IDLE };
    CommentStateType comment_state{ CommentStateType::IDLE };
    CharClass current{ CharClass::NONE };
    CharClass previous{ CharClass::NONE };
    std::array<std::string, 2> token;
    std::size_t line = 1;
    std::size_t column = 0;
    std::size_t start_line = 1;
    std::size_t start_column = 1;

    const auto get_char_class = [](char ch) noexcept -> CharClass {
        return is_space(ch) ? CharClass::WHITESPACE : CharClass::REGULAR;
    };

    const auto char_class_to_int = [](const CharClass& cc) noexcept -> std::int8_t {
        return static_cast<std::int8_t>(cc);
    };

    const auto in_comment = [&comment_state]() noexcept -> bool {
        return (comment_state == CommentStateType::SINGLE_LINE) || (comment_state == CommentStateType::OPEN) || (comment_state == CommentStateType::MAY_CLOSE);
    };

    const auto in_string = [&string_state]() noexcept -> bool {
        return (string_state == StringStateType::IN_STRING) || (string_state == StringStateType::MAY_CLOSE);
    };

    while (!stream.eof()) {
        stream.get(ch);
        if (stream.eof()) {
            LineNumbers line_numbers{ start_line, start_column, line, column - 1 };
            TokenType tt{};
            if (current == CharClass::WHITESPACE) {
                tt = TokenType::WHITESPACE;
            } else if (current == CharClass::REGULAR) {
                tt = TokenType::REGULAR;
            }
            co_yield{ Token(tt, line_numbers, token[char_class_to_int(current)]) };   // TODO: FIX ME!!!
        }
        column++;
        current = get_char_class(ch);
        if (comment_state == CommentStateType::MAY_START) {
            if (ch == SLASH) {
                comment_state = CommentStateType::SINGLE_LINE;
            }
            else if (ch == ASTERIX) {
                comment_state = CommentStateType::OPEN;
            }
            else {
                comment_state = CommentStateType::IDLE;
            }
        }
        else if ((comment_state == CommentStateType::OPEN) && (ch == ASTERIX)) {
            comment_state = CommentStateType::MAY_CLOSE;
        }
        else if ((comment_state == CommentStateType::MAY_CLOSE)) {
            if (ch == SLASH) {
                token[char_class_to_int(CharClass::REGULAR)].push_back(ch);
                for (const auto& elem : split_multi_line_comment(token[char_class_to_int(CharClass::REGULAR)], start_line, start_column, line, column - 1)) {
                    co_yield{ elem };
                }
                token[char_class_to_int(CharClass::REGULAR)].clear();
                comment_state = CommentStateType::IDLE;
                start_column = column + 1;
                start_line = line;
                continue;
            }
            else if (ch != ASTERIX) {
                comment_state = CommentStateType::OPEN;
            }
        }
        if ((ch == SLASH) && !in_comment()) {
            if (comment_state == CommentStateType::IDLE) {
                comment_state = CommentStateType::MAY_START;
            }
        }
        if (!in_comment()) {
            if (ch == DQUOTE) {
                if (string_state == StringStateType::IDLE) {
                    string_state = StringStateType::IN_STRING;
                }
                else if (string_state == StringStateType::IN_STRING) {
                    string_state = StringStateType::MAY_CLOSE;
                }
                else {
                    string_state = StringStateType::IN_STRING;
                    auto& tk = token[char_class_to_int(CharClass::STRING)];
                    tk[tk.length() - 1] = '\\';
                }
            }
            else if (string_state == StringStateType::MAY_CLOSE) {
                string_state = StringStateType::IDLE;
            }
        }
        if (previous == CharClass::NONE) {
            token[char_class_to_int(current)].push_back(ch);
        }
        else {
            if (previous == current) {
                if ((string_state == StringStateType::IDLE) && (!in_comment())) {
                    token[char_class_to_int(current)].push_back(ch);
                }
                else {
                    token[char_class_to_int(CharClass::STRING)].push_back(ch);
                }
            }
            else {
                if (in_string() || in_comment()) {
                    token[char_class_to_int(CharClass::STRING)].push_back(ch);
                    if (token[char_class_to_int(CharClass::WHITESPACE)].length()) {
                        if (!supress_whitespace) {
                            LineNumbers line_numbers{ start_line, start_column, line, column - 1 };
                            co_yield{ Token(TokenType::WHITESPACE, line_numbers, token[char_class_to_int(CharClass::WHITESPACE)]) };
                        }
                        token[char_class_to_int(CharClass::WHITESPACE)].clear();
                        start_column++;
                    }
                }
                else {
                    auto line_numbers{ LineNumbers(start_line, start_column, line, column - 1) };
                    if (current == CharClass::REGULAR) {
                        token[char_class_to_int(CharClass::REGULAR)].push_back(ch);
                        if (!supress_whitespace) {
                            LineNumbers line_numbers{ start_line, start_column, line, column - 1 };
                            co_yield{ Token(TokenType::WHITESPACE, line_numbers, token[char_class_to_int(CharClass::WHITESPACE)]) };
                        }
                        token[char_class_to_int(CharClass::WHITESPACE)].clear();
                    }
                    else {
                        token[char_class_to_int(CharClass::WHITESPACE)].push_back(ch);
                        LineNumbers line_numbers{ start_line, start_column, line, column - 1 };
                        if (token[char_class_to_int(CharClass::REGULAR)] != "") {
                            co_yield{ Token(TokenType::REGULAR, line_numbers, token[char_class_to_int(CharClass::REGULAR)]) };
                        }
                        token[char_class_to_int(CharClass::REGULAR)].clear();
                    }
                    start_line = line;
                    start_column = column;
                }
            }
        }
        previous = current;
        previous_ch = ch;
        if (ch == NL) {
            line++;
            column = 0;
            string_state = StringStateType::IDLE;   // Unterminated string?
            if (comment_state == CommentStateType::SINGLE_LINE) {
                comment_state = CommentStateType::IDLE;

                for (const auto& elem : split_single_line_comment(token[char_class_to_int(CharClass::REGULAR)], start_line, start_column)) {
                    co_yield{ elem };
                }
                token[char_class_to_int(CharClass::REGULAR)].clear();
            }
        }
        else if (ch == CR) {
            column = 1;
        }
    }
}
