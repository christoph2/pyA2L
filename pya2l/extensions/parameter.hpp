
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
        m_type(type), m_name(name), m_multiple(false), m_tuple{ false }, m_enumerators{ values } {
    }

    // Tuples.
    Parameter(const tuple_element_t& counter, const std::vector< tuple_element_t>& elements) :
        m_type(PredefinedType::Tuple), m_multiple(false), m_tuple{ true }, m_counter{ counter }, m_tuple_elements{ elements } {
        std::cout << "TUPLE!!!\n";
    }

    ~Parameter() noexcept = default;

    bool validate(const ANTLRToken* token, const AsamVariantType& value) const {
        bool ok{ false };

        if (std::size(m_enumerators) == 0) {
            const auto entry = SPRUNG_TABELLE[std::bit_cast<std::uint16_t>(m_type) - 1];
            ok               = entry->validate(value);
            return ok;
        } else {
            ok = m_enumerators.contains(std::get<std::string>(value));
            if (!ok) {
                std::cout << token->line() << ":" << token->column() << ": error : "
                          << "Enumeration '" + m_name + "' must be one of: " << valid_enumerators(m_enumerators) << " -- got: '"
                          << std::get<std::string>(value) << "'." << std::endl;
            }
            return ok;
        }
    }

    bool expected_token(const ANTLRToken* token) const {
        const auto entry = SPRUNG_TABELLE[std::bit_cast<std::uint16_t>(m_type) - 1];
        return entry->m_valid_tokens.contains(static_cast<A2LTokenType>(token->getType()));
    }

    AsamVariantType convert(std::string_view text) const {
        unsigned long long res_u{ 0 };
        signed long long   res_s{ 0 };
        switch (m_type) {
            case PredefinedType::Int:
            case PredefinedType::Long:
                if ((text.length() > 2) && ((text[0] == '0') && (text[1] == 'x'))) {
                    return static_cast<signed long long>(std::strtoll(text.data(), nullptr, 16));
                } else {
                    return static_cast<signed long long>(std::strtoll(text.data(), nullptr, 10));
                }
            case PredefinedType::Uint:
            case PredefinedType::Ulong:
                if ((text.length() > 2) && ((text[0] == '0') && (text[1] == 'x'))) {
                    return static_cast<unsigned long long>(std::strtoll(text.data(), nullptr, 16));
                } else {
                    return static_cast<unsigned long long>(std::strtoll(text.data(), nullptr, 10));
                }
            case PredefinedType::Float:
                return std::strtold(text.data(), nullptr);
            default:
                return text.data();
        }
    #if 0


    String     = 6,
    Enum       = 7,
    Ident      = 8,
    Datatype   = 9,
    Indexorder = 10,
    Addrtype   = 11,
    Byteorder  = 12,
    Datasize   = 13,
    Linktype   = 14,
    Tuple      = 15,
    #endif
    }

    // private:
   public:

    PredefinedType                 m_type;
    std::string                    m_name;
    bool                           m_multiple;
    bool                           m_tuple;
    std::set<std::string>          m_enumerators;
    std::optional<tuple_element_t> m_counter;
    std::vector< tuple_element_t>  m_tuple_elements{};
};

#endif  // __PARAMETER_HPP
