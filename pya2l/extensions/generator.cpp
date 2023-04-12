

#include "generator.hpp"


bool is_space(char ch) {
    if ((ch == '\t') || (ch == '\n') || (ch == '\v') || (ch == '\f') || (ch == '\r') || (ch == '\x20')) {
        return true;
    }
    return false;
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
    std::size_t column = 1;
    std::size_t start_line = 0;
    std::size_t start_column = 0;

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
            co_yield { current, token[char_class_to_int(current)] };
        }
        if (ch == NL) {
            line++;
            column = 1;
            string_state = StringStateType::IDLE;   // Unterminated string?
            if (comment_state == CommentStateType::SINGLE_LINE) {
                comment_state = CommentStateType::IDLE;
            }
        } else if (ch == CR) {
            column = 1;
        }
        if ((start_line == 0) && (start_column == 0)) {
            start_line = line;
            start_column = column;
        }
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
        } else if ((comment_state == CommentStateType::MAY_CLOSE)) {
            if (ch == SLASH) {
                comment_state = CommentStateType::IDLE;
            } else {
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
                } else if (string_state == StringStateType::IN_STRING) {
                    string_state = StringStateType::MAY_CLOSE;
                } else {
                    string_state = StringStateType::IN_STRING;
                    auto& tk = token[char_class_to_int(CharClass::STRING)];
                    tk[tk.length() - 1] = '\\';
                }
            } else if (string_state == StringStateType::MAY_CLOSE) {
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
                }
                else {
                    auto line_numbers{ LineNumbers(start_line, start_column, line, column - 1) };
                    if (current == CharClass::REGULAR) {
                        token[char_class_to_int(CharClass::REGULAR)].push_back(ch);
                        if (!supress_whitespace) {
                            co_yield{ current, token[char_class_to_int(CharClass::WHITESPACE)] };
                        }
                        token[char_class_to_int(CharClass::WHITESPACE)].clear();
                    } else {
                        token[char_class_to_int(CharClass::WHITESPACE)].push_back(ch);
                        co_yield{ current, token[char_class_to_int(CharClass::REGULAR)] };
                        token[char_class_to_int(CharClass::REGULAR)].clear();
                    }
                    start_line = 0;
                    start_column = 0;
                }
            }
        }
        previous = current;
        column++;
        previous_ch = ch;
    }
}

const char* THE_MESSAGE{ "\tHello\t\t \t\nworld!!!\r /*commenty-vibes-mofakahh!!!*/A" };

void dumper(std::vector<std::string>&& result) {

    std::cout << "-------------------------------------------------" << std::endl;
    for (const auto& r : result) {
        std::cout << "\t" << r << std::endl;
    }
    std::cout << "-------------------------------------------------\n" << std::endl;
}

int main() {
    //std::string FN = "C:\\csProjects\\pyA2L\\examples\\ASAP2_Demo_V161.a2l";
    std::string FN = "C:\\csProjects\\pyA2L\\examples\\HAXNR4000000.a2l";

    std::ifstream stream{FN};

    for (const auto&& r : tokenizer(stream)) {
        std::cout << "'" << std::get<1>(r) << "' " << std::endl;
    }

    return EXIT_SUCCESS;
}
