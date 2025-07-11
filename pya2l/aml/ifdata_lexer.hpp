
#if !defined(__IFDATA_LEXER_HPP)
    #define __IFDATA_LEXER_HPP

    #include <ctre.hpp>
    #include <iostream>
    #include <ranges>
    #include <regex>
    #include <variant>

static const std::regex AML_REGEX{
    R"""(((/\*.*?\*/)|(//.*?$))|(\"[^\"]*?\")|(/begin|/end)|(\b[a-zA-Z_][a-zA-Z_0-9.]*\b)|(\b([+\-]?(\d+([.]\d*)?([eE][+\-]?\d+)?|[.]\d+([eE][+\-]?\d+)?))\b)|(\b((0[xX][0-9a-fA-F]+)|([+\-]?[0-9]+))\b))""",
    std::regex_constants::ECMAScript | std::regex_constants::icase
};

enum class IfDataTokenType : uint8_t {
    NONE    = 0,
    IDENT   = 1,
    FLOAT   = 2,
    INT     = 3,
    COMMENT = 4,
    STRING  = 6,
    BEGIN   = 7,
    END     = 8,
};

using TokenDataType = std::optional<std::variant<int64_t, long double, std::string>>;


std::string token_data_type_to_string(IfDataTokenType value) {
	switch (value) {
		case IfDataTokenType::NONE:
			return "NONE";
		case IfDataTokenType::IDENT:
			return "IDENT";
		case IfDataTokenType::FLOAT:
			return "FLOAT";
		case IfDataTokenType::INT:
			return "INT";
		case IfDataTokenType::COMMENT:
			return "COMMENT";
		case IfDataTokenType::STRING:
			return "STRING";
		case IfDataTokenType::BEGIN:
			return "BEGIN";
		case IfDataTokenType::END:
			return "END";
	}
    return "";
}


std::string value_type_to_string(TokenDataType value) {
	if (value.has_value()) {
		if (std::holds_alternative<int64_t>(*value)) {
			return std::to_string(std::get<int64_t>(*value));
		} else if (std::holds_alternative<long double>(*value)) {
			return std::to_string(std::get<long double>(*value));
		} else if (std::holds_alternative<std::string>(*value)) {
			return std::get<std::string>(*value);
		}
	} else {
		return "<null>";
	}
}


struct IfDataToken {
    IfDataTokenType     type{ IfDataTokenType::NONE };
    TokenDataType value{ std::nullopt };

	std::string to_string() const noexcept {
		std::stringstream ss;
		ss << "Token(type=" << token_data_type_to_string(type) << ", value=" << value_type_to_string(value) << ")";
        return ss.str();
	}

    auto get_type() const noexcept { return type; }
    auto get_value() const noexcept { return value; }

};

auto ifdata_lexer(const std::string& ifdata_section) -> std::vector<IfDataToken> {
    std::smatch match;
    std::string input{ ifdata_section };

    std::vector<IfDataToken> result;

    while (std::regex_search(input, match, AML_REGEX)) {
        auto  idx = 0;
        IfDataToken tok{};
        for (auto x : match) {
            if ((x.matched) && (idx > 0)) {
                const auto& tstr = x.str();
                auto        base = 10;
                switch (idx) {
                    case 1:
                        tok.type  = IfDataTokenType::COMMENT;
                        tok.value = x;
                        break;
                    case 4:
                        tok.type  = IfDataTokenType::STRING;
                        tok.value = x.str().substr(1, std::size(x.str()) - 2);
                        break;
                    case 5:
                        if (tstr == "/end") {
                            tok.type = IfDataTokenType::END;
                        } else {
                            tok.type = IfDataTokenType::BEGIN;
                        }
                        break;
                    case 6:
                        tok.type  = IfDataTokenType::IDENT;
                        tok.value = x;
                        break;
                    case 7:
                    case 0x0d:
                        tok.type = IfDataTokenType::INT;
                        if (tstr.find('.') != std::string::npos) {
                            tok.value = std::strtold(tstr.c_str(), nullptr);
                        } else {
                            if ((tstr.starts_with("0x")) || (tstr.starts_with("0X"))) {
                                base = 16;
                            }
                            tok.value = std::strtoll(tstr.c_str(), nullptr, base);
                        }
                        break;
                    default:
                        std::cout << "ERROR\n";
                        break;
                }
                result.push_back(tok);
                break;
            }
            idx++;
        }
        auto pos    = 0;
        auto suffix = match.suffix().str();
        while (true) {
            auto ch = suffix[pos];
            if (!std::isspace(ch)) {
                break;
            }
            ++pos;
        }
        input = suffix.substr(pos, std::size(suffix));
    }
    return result;
}

#endif  // #define __IFDATA_LEXER_HPP
