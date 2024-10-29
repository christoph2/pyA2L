
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
    #include "parser_table.hpp"
    #include "preprocessor.hpp"
    #include "token_stream.hpp"
    #include "valuecontainer.hpp"

class A2LParser {
   public:

    using value_table_t = std::tuple<std::string, std::string, std::vector<std::vector<AsamVariantType>>>;

    explicit A2LParser(
        std::optional<preprocessor_result_t> prepro_result, const std::string& file_name, const std::string& encoding
    ) :
        m_prepro_result(prepro_result), m_keyword_counter(0), m_table(PARSER_TABLE), m_root("root"), m_finalized(false) {
        kw_push(m_table);
        m_value_stack.push(&m_root);
        m_idr         = std::make_unique<IfDataReader>(std::get<2>(prepro_result.value()));
        m_table_count = 0;
        parse(file_name, encoding);
    }

    A2LParser(const A2LParser&) = delete;

    ~A2LParser() {
        close();
    }

    void close() {
        if (!m_finalized) {
            m_reader->close();
            m_finalized = true;
        }
    }

    void parse(const std::string& file_name, const std::string& encoding) {
        ValueContainer::set_encoding(encoding);
        std::optional<std::string> if_data_section;
        m_reader = std::make_unique<TokenReader>(file_name);
        if (m_prepro_result) {
            auto idr = std::get<2>(m_prepro_result.value());
            idr.open();
        }
        while (true) {
            const auto token = m_reader->LT(1);

            if (token_type() == A2LTokenType::BEGIN) {
                m_reader->consume();
    #if 0
                if (kw_tos().contains(token_type())) {
                } else {
                    std::cout << "Warning: unexpected token: " << token->toString() << std::endl;
                }
    #endif
            }

            // TODO:  Factor out.
            if (token_type() == A2LTokenType::END) {
                m_reader->consume();
                const auto glied = m_reader->LT(1);
                assert(kw_tos().m_name == glied->getText());    // TODO: handle error
                if (kw_tos().m_name == glied->getText()) {
                    kw_pop();
                    m_value_stack.pop();
                }
                m_reader->consume();
                continue;
            }

            if (token->getType() == ANTLRToken::_EOF) {
                if (std::size(m_kw_stack) > 1) {
                    std::cout << "[ERROR (pya2l.A2LParser)]    " << "Premature end of file!!!\n";
                } else {
                   // std::cout << "OK, done.\n";
                }
                break;
            }

            if (kw_tos().contains(token->getType())) {
                const auto ttype = kw_tos().get(token->type());
                kw_push(ttype);
                auto& vref = value_tos().add_keyword(ValueContainer(ttype.m_class_name));
                m_value_stack.push(&vref);
            } else {
                //
                // TODO: Addressmapper
                auto kwt = kw_tos();
                std::cerr << "[ERROR (pya2l.A2LParser)]    Invalid token: " << token->toString() << std::endl;
                if ((token->getText() == "IF_DATA") && (kwt.m_name == "ROOT")) {
                    std::cerr << "[ERROR (pya2l.A2LParser)]    No top-level PROJECT element. This is probably an include file?\n";
                }
                break;
            }

            if (token->getText() == "IF_DATA") {
                // std::cout << "\tID: " << token->getLine() << ":" << token->column() << std::endl;
                if (m_prepro_result) {
                    if_data_section = m_idr->get({ token->getLine(), token->column() + 1 });
                    if (if_data_section) {
                        // std::cout << "\t FOUND IF_DATA!!!\n";
                    }
                }
            }
            m_reader->consume();
            m_keyword_counter++;
            auto kw = ValueContainer(kw_tos().m_name);

            // std::cout << "KW: " << kw_tos().m_name << std::endl;

            auto [p, m] = do_parameters();
            value_tos().set_parameters(std::move(p));
            value_tos().set_multiple_values(std::move(m));
            value_tos().set_if_data(std::move(if_data_section));

            if (kw_tos().m_block == false) {
                kw_pop();
                m_value_stack.pop();
            }
            if (token_type() == A2LTokenType::END) {
                m_reader->consume();
                const auto glied = m_reader->LT(1);
                assert(kw_tos().m_name == glied->getText());
                if (kw_tos().m_name == glied->getText()) {
                    kw_pop();
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

                if ((kw_tos().contains(token->getType())) || (kw_tos(1).contains(token->getType())) ||
                    (token_type() == A2LTokenType::BEGIN) ||
                    ((token_type() == A2LTokenType::END) && (parameter.is_multiple() == false))) {
                    // Not all parameters are present.

                    std::cerr << "[WARNING (pya2l.A2LParser)]  " << kw_tos().m_name << " is missing one or more required parameters: " << std::endl;

                    for (std::size_t idx = param_count; idx < std::size(kw_tos().m_parameters); ++idx) {
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
                            if (!std::holds_alternative<std::string>(parameter_list[0])) {
                                std::cerr << "[ERROR (pya2l.A2LParser)]    " << "Invalid tuple.\n";
                                break;
                            }
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

                    auto       token_text = token->getText();
                    const auto param_type = parameter.get_type();
                    using enum PredefinedType;

                    if (((param_type == Int) || (param_type == Uint) || (param_type == Long) || (param_type == Ulong) ||
                         (param_type == Float)) &&
                        ((token_text == "-") || ((token_text == "+")))) {
                        m_reader->consume();
                        auto number_text = m_reader->LT(1)->getText();

                        token_text += number_text;
                    }

                    const auto value = convert(param_type, token_text);

                    const auto valid = validate(parameter, token, value);
                    if (!valid) {
                        std::cout << "[ERROR (pya2l.A2LParser)]    " << "Invalid param: " << parameter.get_name() << " -- " << token->toString() << std::endl;
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

    Keyword& kw_tos(std::size_t pos = 0) {
        const auto offset = std::size(m_kw_stack) - pos - 1;

        return m_kw_stack[offset];
    }

    void kw_push(const Keyword& kw) {
        m_kw_stack.push_back(kw);
    }

    void kw_pop() {
        m_kw_stack.pop_back();
    }

    ValueContainer& value_tos() {
        return *m_value_stack.top();
    }

    A2LTokenType token_type(int k = 1) {
        return static_cast<A2LTokenType>(m_reader->LT(k)->getType());
    }

   private:

    std::optional<preprocessor_result_t> m_prepro_result;
    std::unique_ptr<IfDataReader>        m_idr;
    std::string                          m_encoding;
    std::unique_ptr<TokenReader>         m_reader;
    std::size_t                          m_keyword_counter;
    std::vector<Keyword>                 m_kw_stack;
    std::stack<ValueContainer*>          m_value_stack;
    Keyword&                             m_table;
    ValueContainer                       m_root;
    std::vector<value_table_t>           m_tables;
    std::size_t                          m_table_count{ 0 };
    bool                                 m_finalized{ false };
};

#endif  // __A2LPARSER_HPP
