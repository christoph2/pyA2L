
#if !defined __PARAMETER_HPP
    #define __PARAMETER_HPP

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
        m_tuple{ true }, m_counter{ counter }, m_tuple_elements{ elements } {  // TODO: m_type initialisieren.
        std::cout << "TUPLE!!!\n";
    }

    ~Parameter() noexcept = default;

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

#endif  // __PARAMETER_HPP
