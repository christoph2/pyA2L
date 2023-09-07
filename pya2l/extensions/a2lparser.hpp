
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
    #include <vector>

    #include "a2ltoken.hpp"
    #include "asam_types.hpp"
    #include "token_stream.hpp"

class Parameter {
   public:

    using type_t = enum class ParameterType : std::uint8_t {
        INTEGRAL,
        ENUMERATION,
        TUPLE
    };

    using tuple_element_t = std::tuple<PredefinedType const &, std::string>;

    // Integral types and the like.
    Parameter(PredefinedType type, std::string_view name, bool multiple = false) :
        m_type(type), m_name(name), m_multiple(multiple), m_tuple{ false } {
    }

    // Enumerations.
    Parameter(PredefinedType type, std::string_view name, const std::set<std::string>& values) :
        m_type(type), m_name(name), m_multiple(false), m_tuple{ false }, m_value_stack{ values } {
    }

    // Tuples.
    Parameter(const tuple_element_t& counter, const std::vector< tuple_element_t>& elements) :
        m_tuple{ true }, m_counter{ counter }, m_tuple_elements{ elements } {
        std::cout << "TUPLE!!!\n";
    }

    bool validate(const ANTLRToken* token) const {
        bool result{ false };

        if (std::size(m_value_stack) == 0) {
            const auto entry = SPRUNG_TABELLE[std::bit_cast<std::uint16_t>(m_type) - 1];
            result           = entry->validate(token->getText());
            return result;
        } else {
            result = m_value_stack.contains(token->getText());
            assert(result == true, "Invalid Enumerator!!!");
            return result;
        }
    }

    bool expected_token(const ANTLRToken* token) const {
        const auto entry = SPRUNG_TABELLE[std::bit_cast<std::uint16_t>(m_type) - 1];
        return entry->m_valid_tokens.contains(static_cast<A2LTokenType>(token->getType()));
    }

    // private:
   public:

    PredefinedType                 m_type;
    std::string                    m_name;
    bool                           m_multiple;
    bool                           m_tuple;
    std::set<std::string>          m_value_stack;
    std::optional<tuple_element_t> m_counter;
    std::vector< tuple_element_t>  m_tuple_elements{};
};

class Keyword {
   public:

    using map_t = std::vector<Keyword>;

    Keyword(
        A2LTokenType token, std::string_view name, std::string_view class_name, bool block, bool multiple,
        const std::vector<Parameter>& parameters, const map_t& keywords
    ) :
        m_token(token), m_name(name), m_class_name(class_name), m_block(block), m_multiple(multiple), m_parameters(parameters) {
        for (const auto& kw : keywords) {
            m_keywords.insert({ kw.m_token, kw });
        }
    }

    Keyword()               = default;
    Keyword(const Keyword&) = default;

    bool contains(std::size_t token) const {
        return contains(static_cast<A2LTokenType>(token));
    }

    bool contains(A2LTokenType token) const {
        return m_keywords.contains(token);
    }

    auto get(std::size_t token) const -> Keyword {
        return get(static_cast<A2LTokenType>(token));
    }

    auto get(A2LTokenType token) const -> Keyword {
        return m_keywords.find(token)->second;
    }

    // private:

    A2LTokenType                    m_token;
    std::string                     m_name;
    std::string                     m_class_name;
    bool                            m_block;
    bool                            m_multiple;
    std::vector<Parameter>          m_parameters;
    std::map<A2LTokenType, Keyword> m_keywords;
};

class ValueContainer {
   public:

    using key_value_t      = std::tuple<std::string, std::variant<std::string, unsigned long long, long double>>;
    using key_value_list_t = std::vector< key_value_t>;

    using container_type      = ValueContainer;
    using container_list_type = std::vector<container_type>;

    ValueContainer() = default;

    explicit ValueContainer(std::string_view name) :
        m_name(name),
        m_parameters(),
        m_keywords(){

        };

    explicit ValueContainer(const ValueContainer& other) {
        m_name       = other.m_name;
        m_parameters = other.m_parameters;
        m_keywords   = other.m_keywords;

        // std::ranges::copy(other.m_parameters.begin(), other.m_parameters.end(), std::back_inserter(m_parameters));
        // std::ranges::copy(other.m_keywords.begin(), other.m_keywords.end(), std::back_inserter(m_keywords));
    }

    void set_parameters(key_value_list_t&& parameters) noexcept {
        m_parameters = std::move(parameters);
    }

    void set_parameters(const key_value_list_t& parameters) noexcept {
        m_parameters = parameters;
    }

    auto& add_keyword(/*const*/ container_type& kw) noexcept {
        return m_keywords.emplace_back(kw);
    }

    auto& add_keyword(container_type&& kw) noexcept {
        return m_keywords.emplace_back(kw);
    }

    const auto& get_name() const noexcept {
        return m_name;
    }

    const auto& get_keywords() const noexcept {
        return m_keywords;
    }

    const auto& get_parameters() const noexcept {
        return m_parameters;
    }

    #if 0
    void add_parameter(key_value_t&& parameter) {
        m_parameters.emplace_back(std::move(parameter));
    }
    #endif

    ~ValueContainer() = default;

   private:

    std::string         m_name;
    key_value_list_t    m_parameters;
    container_list_type m_keywords;
};

    #include "parser_table.hpp"

class Parser {
   public:

    explicit Parser(/*std::string_view*/ const std::string& file_name, Keyword& table) :
        m_reader("A2L.tmp"), m_table(table), m_root("root") {
        std::cout << "Parsing file: " << file_name << std::endl;
        m_kw_stack.push(m_table);
        m_value_stack.push(&m_root);
    }

    Parser(const Parser&) = delete;

    void parse() {
        auto idx = 0;

        while (true) {
            const auto token = m_reader.LT(1);
            // auto block = kw_tos().m_block;

            if (token_type() == A2LTokenType::BEGIN) {
                m_reader.consume();
                if (kw_tos().contains(token_type())) {
                    // std::cout << "Token: " << m_reader.LT(1)->kw_tos() << std::endl;
                }
                // m_kw_stack.push(m_table);
                // m_table = m_table.get(tt);
                // idx++;

                // std::cout << "Unexpected token: " << token << ". expected /'begin'." << std::endl;
            }
            // TODO:  Factor out.
            if (token_type() == A2LTokenType::END) {
                m_reader.consume();
                auto glied = m_reader.LT(1);
                // std::cout << "\t/END " << glied->getText() << "\n";
                assert(kw_tos().m_name == glied->getText());
                if (kw_tos().m_name == glied->getText()) {
                    m_kw_stack.pop();
                    m_value_stack.pop();
                }
                m_reader.consume();
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
                // std::cout << idx++ << ": " << token->getText() << std::endl;
                const auto xxx = kw_tos().get(token->type());
                m_kw_stack.push(xxx);
                auto& vref = value_tos().add_keyword(ValueContainer(xxx.m_class_name));
                m_value_stack.push(&vref);
            } else {
                std::cout << "Huch!!!\n";
                throw std::runtime_error("Invalid token");
            }
            m_reader.consume();
            idx++;

    #if 0
            if (token_type() == ANTLRToken::_EOF) {
                // std::numeric_limits<size_t>::max()
                std::cout << idx / 1000 << "k tokens processed." << std::endl;
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
                m_reader.consume();
                auto glied = m_reader.LT(1);
                assert(kw_tos().m_name == glied->getText());
                if (kw_tos().m_name == glied->getText()) {
                    m_kw_stack.pop();
                    m_value_stack.pop();
                }
                m_reader.consume();
            }
        }
    }

    const ValueContainer& get_values() const {
        return m_root;
    }

   protected:

    ValueContainer::key_value_list_t do_parameters() {
        auto done           = false;
        auto parameter_list = ValueContainer::key_value_list_t{};

        for (const auto& parameter : kw_tos().m_parameters) {
            done    = !parameter.m_multiple;
            auto tp = parameter.m_type;
            do {
                auto token = m_reader.LT(1);

                if (parameter.m_tuple) {
                    auto       counter_tp  = parameter.m_counter;
                    auto       tuple_tp    = parameter.m_tuple_elements;
                    const auto tuple_n     = std::size(parameter.m_tuple_elements);
                    auto       column      = 0;
                    auto       idx         = 0;
                    auto       tuple_count = 0;
                    tuple_count            = std::atoi(token->getText().c_str());
                    const auto token_count = tuple_count * tuple_n;
                    m_reader.consume();
                    while (idx < token_count) {
                        token = m_reader.LT(1);
                        // std::cout << "\t" << token->getText();
                        column++;
                        if (column == tuple_n) {
                            column = 0;
                            // std::cout << std::endl;
                        }
                        idx++;
                        // if (idx >= token_count) {
                        //     break;
                        // }
                        m_reader.consume();
                    }
                } else {
                    // std::cout << "\tParameter: " << parameter.m_name << R"( M? )" << parameter.m_multiple << std::endl;
                    // std::cout << "\tValue: " << token->getText() << std::endl;

                    parameter_list.emplace_back(parameter.m_name, token->getText());

                    const auto expected = parameter.expected_token(token);
                    if ((parameter.m_multiple == true) && (!expected)) {
                        done = true;
                        continue;  // TODO: maybe break?
                    }
                    const auto valid = parameter.validate(token);
                    if (!expected) {
                        // std::cout << "Unexpected token!!!\n";
                    }
                    if (!valid) {
                        std::cout << "Invalid param!!!\n";
                    }
                    m_reader.consume();
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
        return static_cast<A2LTokenType>(m_reader.LT(k)->getType());
    }

   private:

    TokenReader                 m_reader;
    std::stack<Keyword>         m_kw_stack;
    std::stack<ValueContainer*> m_value_stack;
    Keyword&                    m_table;
    ValueContainer              m_root;
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
