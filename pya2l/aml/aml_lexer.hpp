
#if !defined(__AML_LEXER_HPP)
#define __AML_LEXER_HPP


//namespace Aml {

#include <iostream>
#include <sstream>
#include <fstream>
#include <ranges>
#include <regex>
#include <variant>

#include "types.hpp"


static const std::regex AML_REGEX{ R"""(((/\*.*?\*/)|(//.*?$))|(\"[^\"]*?\")|(/begin|/end|block|enum|taggedstruct|taggedunion|struct|/include)|([;,=\*\{\}\[\]\(\)])|(char|long|uchar|ulong|int64|uint64|int|uint|double|float|float16)|(\b[a-zA-Z_][a-zA-Z_0-9.]*\b)|(\b([+\-]?(\d+([.]\d*)?([eE][+\-]?\d+)?|[.]\d+([eE][+\-]?\d+)?))\b)|(\b((0[xX][0-9a-fA-F]+)|([+\-]?[0-9]+))\b))""", std::regex_constants::ECMAScript };    // std::regex_constants::ECMAScript, std::regex::extended

enum class AmlTokenType : uint8_t {
    NONE = 0,
    IDENT = 1,
    FLOAT = 2,
    INT = 3,
    COMMENT = 4,
    TAG = 6,
    BEGIN = 7,
    END = 8,
    ENUM = 9,
    STRUCT = 10,
    TAGGED_STRUCT = 11,
    TAGGED_UNION = 12,
    PDT = 13,
    LBRACE = 14,
    RBRACE = 15,
    LPARAN = 16,
    RPARAN = 17,
    LSQ = 18,
    RSQ = 19,
    EQU = 20,
    SEMI = 21,
    COLON = 22,
    STAR = 23,
    BLOCK = 24,
    INCLUDE = 25,
};

using TokenDataType = std::optional<std::variant<int64_t, long double, std::string, AMLPredefinedTypeEnum>>;

struct AmlToken {
    AmlTokenType  type{ AmlTokenType::NONE };
    TokenDataType value{ std::nullopt };
    std::size_t   line{ 0 };
    std::size_t   col{ 0 };
};


inline auto aml_lexer(const std::string& ifdata_section) -> std::vector<AmlToken> {
    std::vector<AmlToken> result;

    std::smatch match;
    std::string input{ ifdata_section };
    size_t      skip{ 0 };
    std::size_t current_line{ 1 };
    std::size_t current_col{ 1 };

    while (std::regex_search(input, match, AML_REGEX)) {
        auto     idx = 0;
        AmlToken tok{};
        tok.line = current_line;
        tok.col  = current_col;
        for (auto x : match) {
            if ((x.matched) && (idx > 0)) {
                const auto& tstr = x.str();
                auto base = 10;
                switch (idx) {
                case 1:
                    tok.type = AmlTokenType::COMMENT;
                    tok.value = x;
                    break;
                case 4: // TAG
                    tok.type = AmlTokenType::TAG;
                    tok.value = x.str().substr(1, std::size(x.str()) - 2);
                    break;
                case 5: // KW
                    if (tstr == "/end") {
                        tok.type = AmlTokenType::END;
                    }
                    else if (tstr == "/begin") {
                        tok.type = AmlTokenType::BEGIN;
                    }
                    else if (tstr == "block") {
                        tok.type = AmlTokenType::BLOCK;
                    }
                    else if (tstr == "enum") {
                        tok.type = AmlTokenType::ENUM;
                    }
                    else if (tstr == "taggedstruct") {
                        tok.type = AmlTokenType::TAGGED_STRUCT;
                    }
                    else if (tstr == "taggedunion") {
                        tok.type = AmlTokenType::TAGGED_UNION;
                    }
                    else if (tstr == "struct") {
                        tok.type = AmlTokenType::STRUCT;
                    } else if (tstr == "/include") {
                        tok.type = AmlTokenType::INCLUDE;
                        skip     = 2;
                    }
                    else {
                        std::cerr << "[ERROR (pya2l.AMLLexer)] Unknown keyword token '" << tstr << "' at line " << current_line << ", col " << current_col << "\n";
                    }
                    break;
                case 6: // PARAN, OP
                    if (tstr == "{") {
                        tok.type = AmlTokenType::LBRACE;
                    }
                    else if (tstr == "}") {
                        tok.type = AmlTokenType::RBRACE;
                    }
                    else if (tstr == "(") {
                        tok.type = AmlTokenType::LPARAN;
                    }
                    else if (tstr == ")") {
                        tok.type = AmlTokenType::RPARAN;
                    }
                    else if (tstr == "[") {
                        tok.type = AmlTokenType::LSQ;
                    }
                    else if (tstr == "]") {
                        tok.type = AmlTokenType::RSQ;
                    }
                    else if (tstr == "*") {
                        tok.type = AmlTokenType::STAR;
                    }
                    else if (tstr == ",") {
                        tok.type = AmlTokenType::COLON;
                    }
                    else if (tstr == ";") {
                        tok.type = AmlTokenType::SEMI;
                    }
                    else if (tstr == "=") {
                        tok.type = AmlTokenType::EQU;
                    }
                    else {
                        std::cerr << "[ERROR (pya2l.AMLLexer)] Unknown operator/punctuation '" << tstr << "' at line " << current_line << ", col " << current_col << "\n";
                    }
                    break;
                case 7: // PDT
                    tok.type = AmlTokenType::PDT;
                    if (tstr == "char") {
                        tok.value = AMLPredefinedTypeEnum::CHAR;
                    }
                    else if (tstr == "int") {
                        tok.value = AMLPredefinedTypeEnum::INT;
                    }
                    else if (tstr == "long") {
                        tok.value = AMLPredefinedTypeEnum::LONG;
                    }
                    else if (tstr == "uchar") {
                        tok.value = AMLPredefinedTypeEnum::UCHAR;
                    }
                    else if (tstr == "uint") {
                        tok.value = AMLPredefinedTypeEnum::UINT;
                    }
                    else if (tstr == "ulong") {
                        tok.value = AMLPredefinedTypeEnum::ULONG;
                    }
                    else if (tstr == "int64") {
                        tok.value = AMLPredefinedTypeEnum::INT64;
                    }
                    else if (tstr == "uint64") {
                        tok.value = AMLPredefinedTypeEnum::UINT64;
                    }
                    else if (tstr == "double") {
                        tok.value = AMLPredefinedTypeEnum::DOUBLE;
                    }
                    else if (tstr == "float") {
                        tok.value = AMLPredefinedTypeEnum::FLOAT;
                    }
                    else if (tstr == "float16") {
                        tok.value = AMLPredefinedTypeEnum::FLOAT16;
                    }
                    break;
                case 8: // IDENT
                    tok.type = AmlTokenType::IDENT;
                    tok.value = x;
                    break;
                case 9: // INT
                case 0x0f:
                    tok.type = AmlTokenType::INT;
                    if (tstr.find('.') != std::string::npos) {
                        tok.value = std::strtold(tstr.c_str(), nullptr);
                    }
                    else {
                        if ((tstr.starts_with("0x")) || (tstr.starts_with("0X"))) {
                            base = 16;
                        }
                        tok.value = std::strtoll(tstr.c_str(), nullptr, base);
                    }
                    break;
                default:
                    std::cerr << "[ERROR (pya2l.AMLLexer)] Unhandled regex group " << idx << " for token '" << x.str() << "' at line " << current_line << ", col " << current_col << "\n";
                    break;

                }
                if (skip == 0) {
                    result.push_back(tok);
                } else {
                    --skip;
                }
                break;
            }
            idx++;
        }

        // Advance line/col tracking over the matched text
        for (char ch : match[0].str()) {
            if (ch == '\n') {
                ++current_line;
                current_col = 1;
            } else {
                ++current_col;
            }
        }
        auto pos    = 0;
        auto suffix = match.suffix().str();
        while (true) {
            auto ch = suffix[pos];
            if (!std::isspace(ch)) {
                break;
            }
            if (ch == '\n') {
                ++current_line;
                current_col = 1;
            } else {
                ++current_col;
            }
            ++pos;
        }
        input = suffix.substr(pos, std::size(suffix));
    }

    return result;
}

inline std::string get_file_content(const std::string& file_name) {
    std::ifstream input{ file_name };
    if (!input.is_open()) {
        throw std::runtime_error("[ERROR (pya2l.AMLLexer)] Could not open AML file: '" + file_name + "'");
    }
    std::stringstream buffer;
    buffer << input.rdbuf();
    if (input.bad()) {
        throw std::runtime_error("[ERROR (pya2l.AMLLexer)] I/O error while reading AML file: '" + file_name + "'");
    }
    return buffer.str();
}

//}   // namespace Aml

#endif // __AML_LEXER_HPP
