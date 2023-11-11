
#if !defined(__A2LPARSER_HPP)
    #define __A2LPARSER_HPP

    #include <algorithm>
    #include <array>
    #include <cstdint>
    #include <cstdlib>
    #include <fstream>
    #include <iostream>
    #include <limits>
    #include <map>
    #include <set>
    #include <sstream>
    #include <stack>
    #include <unordered_map>
    #include <unordered_set>
    #include <variant>
    #include <vector>

using AsamVariantType = std::variant<std::string, unsigned long long, signed long long, long double>;

    #include "a2ltoken.hpp"
    #include "asam_types.hpp"
    #include "keyword.hpp"
    #include "parameter.hpp"
    #include "token_stream.hpp"
    #include "valuecontainer.hpp"

///

    #include "parser_table.hpp"

    #if 0
[INFO (pya2l.Preprocessor)]: Preprocessing and tokenizing '..\..\examples\HAXNR4000000.a2l'.
[INFO (pya2l.DB)]: Parsing pre-processed data ...
    #endif

class A2LParser {
   public:

    using value_table_t = std::tuple<std::string, std::string, std::vector<std::vector<AsamVariantType>>>;

    explicit A2LParser() : m_keyword_counter(0), m_table(PARSER_TABLE), m_root("root") {
        m_kw_stack.push(m_table);
        m_value_stack.push(&m_root);
        m_table_count = 0;
    }

    A2LParser(const A2LParser&) = delete;

    void parse(const std::string& file_name, const std::string& encoding) {
        ValueContainer::set_encoding(encoding);
        m_reader = std::make_unique<TokenReader>(file_name);

        while (true) {
            const auto token = m_reader->LT(1);
            // auto block = kw_tos().m_block;

            if (token_type() == A2LTokenType::BEGIN) {
                m_reader->consume();
                if (kw_tos().contains(token_type())) {
                    // std::cout << "Token: " << m_reader->LT(1)->kw_tos() << std::endl;
                }
                // m_kw_stack.push(m_table);
                // m_table = m_table.get(tt);
                // m_keyword_counter++;

                // std::cout << "Unexpected token: " << token << ". expected /'begin'." << std::endl;
            }
            // TODO:  Factor out.
            if (token_type() == A2LTokenType::END) {
                m_reader->consume();
                auto glied = m_reader->LT(1);
                // std::cout << "\t/END " << glied->getText() << "\n";
                assert(kw_tos().m_name == glied->getText());
                if (kw_tos().m_name == glied->getText()) {
                    m_kw_stack.pop();
                    m_value_stack.pop();
                }
                m_reader->consume();
                continue;
            }

            if (token->getType() == ANTLRToken::_EOF) {
                if (std::size(m_kw_stack) > 1) {
                    std::cout << "Premature end of file!!!\n";
                } else {
                    std::cout << "OK, done.\n";
                }
                break;
            }

            if (kw_tos().contains(token->getType())) {
                // std::cout << m_keyword_counter++ << ": " << token->getText() << std::endl;
                const auto xxx = kw_tos().get(token->type());
                m_kw_stack.push(xxx);
                auto& vref = value_tos().add_keyword(ValueContainer(xxx.m_class_name));
                m_value_stack.push(&vref);
            } else {
                std::cout << "Huch!!!\n";
                throw std::runtime_error("Invalid token");
            }
            m_reader->consume();
            m_keyword_counter++;

    #if 0
            if (token_type() == ANTLRToken::_EOF) {
                std::cout << m_keyword_counter / 1000 << "k tokens processed." << std::endl;
                break;
            }
    #endif
            auto kw = ValueContainer(kw_tos().m_name);

            value_tos().set_parameters(do_parameters());

            if (kw_tos().m_block == false) {
                m_kw_stack.pop();
                m_value_stack.pop();
            }
            if (token_type() == A2LTokenType::END) {
                m_reader->consume();
                auto glied = m_reader->LT(1);
                assert(kw_tos().m_name == glied->getText());
                if (kw_tos().m_name == glied->getText()) {
                    m_kw_stack.pop();
                    m_value_stack.pop();
                }
                m_reader->consume();
            }
        }
    }

    const std::vector<value_table_t>& get_tables() const {
        return m_tables;
    }

    const ValueContainer& get_values() const {
        return m_root;
    }

    std::size_t get_keyword_counter() const {
        return m_keyword_counter;
    }

   protected:

    ValueContainer::key_value_list_t do_parameters() {
        auto done           = false;
        auto parameter_list = ValueContainer::key_value_list_t{};

        for (const auto& parameter : kw_tos().m_parameters) {
            done = !parameter.is_multiple();
            do {
                auto token = m_reader->LT(1);

                if (parameter.is_tuple()) {
                    auto tuple_parser = ParameterTupleParser(parameter);
                    tuple_parser.feed(token);
                    m_reader->consume();
                    while (true) {  // TODO: check for \end.
                        token = m_reader->LT(1);
                        tuple_parser.feed(token);
                        if (tuple_parser.get_state() == ParameterTupleParser::StateType::FINISHED) {
                            m_tables.push_back({ value_tos().get_name(), std::get<std::string>(parameter_list[0]),
                                                 tuple_parser.get_table() });
                            m_reader->consume();
                            break;
                        }
                        m_reader->consume();
                    }
                } else {
                    if ((parameter.is_multiple() == true) && (token_type() == A2LTokenType::END)) {
                        done = true;
                        continue;
                    }
                    auto value = convert(parameter.get_type(), token->getText());
                    parameter_list.emplace_back(value);

                    const auto valid = validate(parameter, token, value);
                    if (!valid) {
                        auto f = 10;
                        // std::cout << "Invalid param!!!" << "\n ";
                    }
                    m_reader->consume();
                }
            } while (!done);
        }
        return parameter_list;
    }

    Keyword& kw_tos() {
        return m_kw_stack.top();
    }

    ValueContainer& value_tos() {
        return *m_value_stack.top();
    }

    A2LTokenType token_type(int k = 1) {
        return static_cast<A2LTokenType>(m_reader->LT(k)->getType());
    }

   private:

    std::string                  m_encoding;
    std::unique_ptr<TokenReader> m_reader;
    std::size_t                  m_keyword_counter;
    std::stack<Keyword>          m_kw_stack;
    std::stack<ValueContainer*>  m_value_stack;
    Keyword&                     m_table;
    ValueContainer               m_root;
    std::vector<value_table_t>   m_tables;
    std::size_t                  m_table_count{ 0 };
};

// helper function to print a tuple of any size
template<class Tuple, std::size_t N>
struct TuplePrinter {
    static void print(const Tuple& t) {
        TuplePrinter<Tuple, N - 1>::print(t);
        std::cout << ", " << std::get<N - 1>(t);
    }
};

template<class Tuple>
struct TuplePrinter<Tuple, 1> {
    static void print(const Tuple& t) {
        std::cout << std::get<0>(t);
    }
};

template<typename... Args, std::enable_if_t<sizeof...(Args) == 0, int> = 0>
void print(const std::tuple<Args...>& t) {
    std::cout << "()\n";
}

template<typename... Args, std::enable_if_t<sizeof...(Args) != 0, int> = 0>
void print(const std::tuple<Args...>& t) {
    std::cout << "(";
    TuplePrinter<decltype(t), sizeof...(Args)>::print(t);
    std::cout << ")\n";
}
#endif  // __A2LPARSER_HPP
