/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

    (C) 2023-2024 by Christoph Schueler <cpu12.gems.googlemail.com>

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

#include <cstring>
#include <iomanip>

#include "logger.hpp"


std::vector<Token> split_by_new_line(std::string_view line, std::size_t start_line, std::size_t start_column) {
    auto set_line_numbers = [](LineNumbers &l, std::size_t sl, std::size_t sc, std::size_t el, std::size_t ec) {
        l.start_line = sl;
        l.start_col  = sc;
        l.end_line   = el;
        l.end_col    = ec;
    };

    char const        *cstr     = line.data();
    char const * const START    = line.data();
    const int64_t LAST_IDX = line.length() - 1;

    if (LAST_IDX < 1) {
        return std::vector<Token>{
            Token(TokenClass::WHITESPACE, LineNumbers(start_line, start_column, start_line, start_column), line)
        };
    }
    if (line.find('\n') == std::string::npos) {
        return std::vector<Token>{
            Token(TokenClass::WHITESPACE, LineNumbers(start_line, start_column, start_line, start_column + line.length() - 1), line)
        };
    }

    int64_t       pos  = 0;
    int64_t       prev = -1;
    auto               row  = start_line;
    LineNumbers        line_numbers{};
    std::vector<Token> result;
    using enum TokenClass;

    do {
        cstr = std::strstr(cstr, "\n");
        if (cstr) {
            pos = cstr - START;
            if (prev == -1) {
                if (pos > 0) {
                    set_line_numbers(line_numbers, row, start_column, row, start_column + pos - 1);
                    result.emplace_back(WHITESPACE, line_numbers, line.substr(0, pos));
                    set_line_numbers(line_numbers, row, start_column + pos, row, start_column + pos);
                    result.emplace_back(WHITESPACE, line_numbers, "\n");
                    row++;
                } else {
                    set_line_numbers(line_numbers, row, start_column, row, start_column);
                    result.emplace_back(WHITESPACE, line_numbers, "\n");
                    row++;
                }
            } else {
                if ((pos - prev) > 1) {
                    auto start  = prev + 1;
                    auto length = pos - prev - 1;
                    set_line_numbers(line_numbers, row, 1, row, length);
                    result.emplace_back(WHITESPACE, line_numbers, line.substr(start, length));
                    set_line_numbers(line_numbers, row, prev + length, row, prev + length);
                    result.emplace_back(WHITESPACE, line_numbers, line.substr(prev + length + 1, 1));
                    row++;
                } else {
                    set_line_numbers(line_numbers, row, 1, row, 1);
                    result.emplace_back(WHITESPACE, line_numbers, line.substr(pos, 1));
                    row++;
                }
            }
            cstr++;
            prev = pos;
        }
    } while (cstr && *cstr);
    if (pos < LAST_IDX) {
        set_line_numbers(line_numbers, row, 1, row, LAST_IDX - pos);
        result.emplace_back(WHITESPACE, line_numbers, line.substr(pos + 1));
    }
    return result;
}

auto split_single_line_comment(std::string_view line, std::size_t start_line, std::size_t start_column) {
    std::string::size_type pos = line.find("//");
    std::vector<Token>     result;
    using enum TokenClass;

    if (pos > 0) {
        LineNumbers line_numbers{ start_line, start_column, start_line, start_column + pos - 1 };
        result.emplace_back(REGULAR, line_numbers, line.substr(0, pos));
        line_numbers = { start_line, start_column + pos, start_line, line.length() - pos };
        result.emplace_back(COMMENT, line_numbers, line.substr(pos, line.length() - pos - 1));
        line_numbers = { start_line, line.length() - pos + 1, start_line, line.length() - pos + 1 };
        result.emplace_back(WHITESPACE, line_numbers, "\n");
    } else {
        LineNumbers line_numbers{ start_line, start_column, start_line, line.length() - 1 };
        result.emplace_back(COMMENT, line_numbers, line.substr(0, line.length() - 1));
        line_numbers = { start_line, line.length(), start_line, line.length() };
        result.emplace_back(WHITESPACE, line_numbers, "\n");
    }
    return result;
}

auto split_multi_line_comment(
    std::string_view line, std::size_t start_line, std::size_t start_column, std::size_t end_line, std::size_t end_column
) {
    std::string::size_type start_pos = line.find("/*");
    std::vector<Token>     result;
    using enum TokenClass;

    if (start_pos > 0) {
        LineNumbers line_numbers{ start_line, start_column, start_line, start_column + start_pos - 1 };
        result.emplace_back(REGULAR, line_numbers, line.substr(0, start_pos));
        line_numbers = { start_line, start_column + start_pos, start_line, line.length() };
        result.emplace_back(COMMENT, line_numbers, line.substr(start_pos, line.length() - start_pos));
    } else {
        LineNumbers line_numbers = { start_line, start_column + start_pos, end_line, end_column + 1 };
        result.emplace_back(COMMENT, line_numbers, line);
    }

    return result;
}

Generator<TokenizerReturnType> tokenizer(std::basic_istream<char> &stream, bool supress_whitespace) {
    char                       ch{ '\x00' };
    char                       previous_ch{ '\x00' };
    StringStateType            string_state{ StringStateType::IDLE };
    CommentStateType           comment_state{ CommentStateType::IDLE };
    CharClass                  current{ CharClass::NONE };
    CharClass                  previous{ CharClass::NONE };
    std::array<std::string, 2> token;
    std::size_t                line              = 1;
    std::size_t                column            = 0;
    std::size_t                start_line        = 1;
    std::size_t                start_column      = 1;
    bool                       string_class      = false;
    bool                       multi_line_string = false;
    auto logger = create_logger("tokenizer");

    const auto get_char_class = [](char ch) noexcept {
        return is_space(ch) ? CharClass::WHITESPACE : CharClass::REGULAR;
    };

    constexpr auto char_class_to_int = [](const CharClass &cc) noexcept {
        return static_cast<int8_t>(cc);
    };

    const auto in_comment = [&comment_state]() noexcept {
        using enum CommentStateType;
        return (comment_state == SINGLE_LINE) || (comment_state == OPEN) || (comment_state == MAY_CLOSE);
    };

    const auto in_string = [&string_state]() noexcept {
        return (string_state == StringStateType::IN_STRING) || (string_state == StringStateType::MAY_CLOSE);
    };

    auto regular_double_quote = [&token, &char_class_to_int]() noexcept {
        const auto &token_str = token[char_class_to_int(CharClass::REGULAR)].c_str();
        const auto  token_length = std::strlen(token_str);
        const auto  previous_ch   = token_str[token_length - 1];
        auto        previous_bs   = (previous_ch == BSLASH);
        if (token_length >= 2) {
            const auto prev_previous_ch = token_str[token_length - 2];
            auto       prev_previous_bs    = (prev_previous_ch == BSLASH);
            if (token_length >= 3) {
                const auto prev_prev_previous_ch = token_str[token_length - 3];
                auto       prev_prev_previous_bs = (prev_prev_previous_ch == BSLASH);
                if (prev_prev_previous_bs && prev_previous_bs && previous_bs) {
                    return false;
                }

            }
            if (prev_previous_bs && previous_bs) {
                return true;    // Escaped back-slash.
            }
        }
        return previous_ch != BSLASH;    // Escaped " or not.
    };

    while (!stream.eof()) {
        stream.get(ch);
        if (stream.eof()) {
            LineNumbers line_numbers{ start_line, start_column, line, column - 1 };
            if (current == CharClass::WHITESPACE) {
                if (token[char_class_to_int(CharClass::WHITESPACE)] == "\n") {
                    line_numbers.end_line = line_numbers.start_line;
                    line_numbers.end_col  = line_numbers.start_col;
                }
                for (const auto &elem :
                     split_by_new_line(token[char_class_to_int(CharClass::WHITESPACE)], start_line, start_column)) {
                    co_yield { elem };
                }
            } else if (current == CharClass::REGULAR) {
                co_yield { Token(TokenClass::REGULAR, line_numbers, token[char_class_to_int(current)]) };
            }
        }
        column++;
        current = get_char_class(ch);
        if (comment_state == CommentStateType::MAY_START) {
            if (ch == SLASH) {
                comment_state = CommentStateType::SINGLE_LINE;
            } else if (ch == ASTERIX) {
                comment_state = CommentStateType::OPEN;
            } else {
                comment_state = CommentStateType::IDLE;
            }
        } else if ((comment_state == CommentStateType::OPEN) && (ch == ASTERIX)) {
            comment_state = CommentStateType::MAY_CLOSE;
        } else if (comment_state == CommentStateType::MAY_CLOSE) {
            if (ch == SLASH) {
                token[char_class_to_int(CharClass::REGULAR)].push_back(ch);
                for (const auto &elem : split_multi_line_comment(
                         token[char_class_to_int(CharClass::REGULAR)], start_line, start_column, line, column - 1
                     )) {
                    co_yield { elem };
                }
                token[char_class_to_int(CharClass::REGULAR)].clear();
                comment_state = CommentStateType::IDLE;
                start_column  = column + 1;
                start_line    = line;
                continue;
            } else if (ch != ASTERIX) {
                comment_state = CommentStateType::OPEN;
            }
        }
        if ((ch == SLASH) && (!in_comment()) && (!in_string())) {
            if (comment_state == CommentStateType::IDLE) {
                comment_state = CommentStateType::MAY_START;
            }
        }
        if (!in_comment()) {
            if (ch == DQUOTE) {
                if (string_state == StringStateType::IDLE) {
                    string_state = StringStateType::IN_STRING;
                    string_class = true;
                } else if ((string_state == StringStateType::IN_STRING) && regular_double_quote()) {
                    string_state = StringStateType::MAY_CLOSE;
                } else {
                    string_state        = StringStateType::IN_STRING;
                    auto &tk            = token[char_class_to_int(CharClass::STRING)];
                    tk[tk.length() - 1] = '\\';
                }
            } else if (string_state == StringStateType::MAY_CLOSE) {
                multi_line_string = false;
                string_state      = StringStateType::IDLE;
            }
        }
        if (previous == CharClass::NONE) {
            token[char_class_to_int(current)].push_back(ch);
        } else {
            if (previous == current) {
                if ((string_state == StringStateType::IDLE) && (!in_comment())) {
                    if (previous_ch == DQUOTE) {
                        LineNumbers line_numbers{ start_line, start_column, line, column - 1 };
                        co_yield { Token(TokenClass::STRING, line_numbers, token[char_class_to_int(current)]) };
                        token[char_class_to_int(CharClass::REGULAR)].clear();
                        string_class = false;
                    }
                    token[char_class_to_int(current)].push_back(ch);
                } else {
                    auto sz = std::size(token[char_class_to_int(CharClass::STRING)]);
                    if ((sz == 1) && (ch == DQUOTE) && (previous == CharClass::REGULAR) &&
                        (string_state == StringStateType::IN_STRING)) {
                        // Get rid of " prefixes, eg. ("some string"
                        LineNumbers line_numbers{ start_line, start_column, line, column - 1 };
                        co_yield { Token(TokenClass::REGULAR, line_numbers, token[char_class_to_int(current)]) };
                        token[char_class_to_int(CharClass::REGULAR)].clear();
                    }
                    token[char_class_to_int(CharClass::STRING)].push_back(ch);
                }
            } else {
                if (in_string() || in_comment()) {
                    token[char_class_to_int(CharClass::STRING)].push_back(ch);
                    if (token[char_class_to_int(CharClass::WHITESPACE)].length()) {
                        if (!supress_whitespace) {
                            LineNumbers line_numbers{ start_line, start_column, line, column - 1 };
                            for (const auto &elem :
                                 split_by_new_line(token[char_class_to_int(CharClass::WHITESPACE)], start_line, start_column)) {
                                co_yield { elem };
                            }
                        }
                        token[char_class_to_int(CharClass::WHITESPACE)].clear();
                        start_column++;
                    }
                } else {
                    auto line_numbers{ LineNumbers(start_line, start_column, line, column - 1) };
                    if (current == CharClass::REGULAR) {
                        token[char_class_to_int(CharClass::REGULAR)].push_back(ch);
                        if (!supress_whitespace) {
                            if (token[char_class_to_int(CharClass::WHITESPACE)] == "\n") {
                                line_numbers = { start_line, start_column, start_line, start_column };
                            } else {
                                line_numbers = { start_line, start_column, line, column - 1 };
                            }
                            for (const auto &elem :
                                 split_by_new_line(token[char_class_to_int(CharClass::WHITESPACE)], start_line, start_column)) {
                                co_yield { elem };
                            }
                        }
                        token[char_class_to_int(CharClass::WHITESPACE)].clear();
                    } else {
                        token[char_class_to_int(CharClass::WHITESPACE)].push_back(ch);
                        line_numbers = { start_line, start_column, line, column - 1 };
                        if (token[char_class_to_int(CharClass::REGULAR)] != "") {
                            co_yield { Token(
                                string_class ? TokenClass::STRING : TokenClass::REGULAR, line_numbers,
                                token[char_class_to_int(CharClass::REGULAR)]
                            ) };
                        }
                        string_class = false;
                        token[char_class_to_int(CharClass::REGULAR)].clear();
                    }
                    start_line   = line;
                    start_column = column;
                }
            }
        }
        previous   = current;
        previous_ch = ch;
        if (ch == NL) {
            line++;
            column = 0;

            if ((multi_line_string == false) &&
                ((string_state == StringStateType::IN_STRING) || (string_state == StringStateType::MAY_CLOSE))) {
                logger->debug("Multiline string @line: {}", line - 1);
                multi_line_string = true;
            }
            if (comment_state == CommentStateType::SINGLE_LINE) {
                comment_state = CommentStateType::IDLE;

                for (const auto &elem :
                     split_single_line_comment(token[char_class_to_int(CharClass::REGULAR)], start_line, start_column)) {
                    co_yield { elem };
                }
                token[char_class_to_int(CharClass::REGULAR)].clear();
            }
        } else if (ch == CR) {
            column = 1;
        }
    }
}
