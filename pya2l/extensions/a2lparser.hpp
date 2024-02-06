
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

    #include "preprocessor.hpp"

    #include "parser_table.hpp"

class A2LParser {
   public:

    using value_table_t = std::tuple<std::string, std::string, std::vector<std::vector<AsamVariantType>>>;

    explicit A2LParser(std::optional<preprocessor_result_t> prepro_result) : m_prepro_result(prepro_result), m_keyword_counter(0), m_table(PARSER_TABLE), m_root("root") {
        m_kw_stack.push(m_table);
        m_value_stack.push(&m_root);
        m_table_count = 0;
    }

    A2LParser(const A2LParser&) = delete;

    void parse(const std::string& file_name, const std::string& encoding) {
        ValueContainer::set_encoding(encoding);
        m_reader = std::make_unique<TokenReader>(file_name);

        if (m_prepro_result) {
            auto idr = std::get<2>(m_prepro_result.value());
            idr.open();
        }


        while (true) {
            const auto token = m_reader->LT(1);
            // auto block = kw_tos().m_block;

            if (token_type() == A2LTokenType::BEGIN) {
                m_reader->consume();
                if (kw_tos().contains(token_type())) {
                }
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
                // std::cout << v++ << ": " << token->getText() << std::endl;
                const auto ttype = kw_tos().get(token->type());
                m_kw_stack.push(ttype);
                auto& vref = value_tos().add_keyword(ValueContainer(ttype.m_class_name));
                m_value_stack.push(&vref);
            } else {
                //
                // TODO: Addressmapper
                //auto msg {"[INFO (pya2l.parser)]"};
                auto msg {""};
                throw std::runtime_error("Invalid token" + std::to_string(token->getLine()) + std::to_string(token->column()) + std::to_string(token->getType()));
            }
            if (token->getText() == "IF_DATA") {
                std::cout << "\tID: " << token->getLine() << ":" << token->column() << std::endl;
                if (m_prepro_result) {
                    auto idr = std::get<2>(m_prepro_result.value());
//#if 0
                    auto res = idr.get({token->getLine(), token->column() + 1});
                    if (res) {
                        std::cout << "\t FOUND IF_DATA!!!\n";
                    }
//#endif
                }
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

            auto [p, m] = do_parameters();
            value_tos().set_parameters(std::move(p));
            value_tos().set_multiple_values(std::move(m));

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

    auto do_parameters() -> std::tuple<ValueContainer::key_value_list_t, std::vector<AsamVariantType>>

    {
        auto                         done           = false;
        auto                         parameter_list = ValueContainer::key_value_list_t{};
        std::vector<AsamVariantType> m_multiple_values;
        auto                         param_count = 0;

        for (const auto& parameter : kw_tos().m_parameters) {
            done = !parameter.is_multiple();
            do {
                auto token = m_reader->LT(1);

                if (kw_tos().contains(token->getType())) {
                    // Not all parameters are present.
                    std::cerr << kw_tos().m_name << " is missing one or more required parameters:" << std::endl;

                    for (auto idx = param_count; idx < std::size(kw_tos().m_parameters); ++idx) {
                        auto p = kw_tos().m_parameters[idx];

                        std::cerr << "\t" << p.get_name() << std::endl;

                        switch (p.get_type()) {
                            case PredefinedType::Int:
                            case PredefinedType::Uint:
                            case PredefinedType::Long:
                            case PredefinedType::Ulong:
                                parameter_list.push_back(0);
                                break;

                            case PredefinedType::Float:
                                parameter_list.push_back(0.0);
                                break;

                            default:
                                parameter_list.push_back("");
                                break;
                        }
                    }
                    return { parameter_list, m_multiple_values };
                }
                param_count++;

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

                    const auto valid = validate(parameter, token, value);
                    if (!valid) {
                        std::cout << "Invalid param!!!"
                                  << "\n ";
                    }

                    if (parameter.is_multiple() == true) {
                        m_multiple_values.emplace_back(value);
                    } else {
                        parameter_list.emplace_back(value);
                    }
                    m_reader->consume();
                }
            } while (!done);
        }
        return { parameter_list, m_multiple_values };
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
    std::optional<preprocessor_result_t> m_prepro_result;
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
