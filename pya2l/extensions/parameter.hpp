
#if !defined __PARAMETER_HPP
    #define __PARAMETER_HPP

    #include "token_stream.hpp"

#include "logger.hpp"


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
    Parameter(const tuple_element_t& counter, const std::vector<tuple_element_t>& elements) :
        m_type(PredefinedType::Tuple), m_multiple(false), m_tuple{ true }, m_counter{ counter }, m_tuple_elements{ elements } {
    }

    virtual ~Parameter() noexcept = default;

    PredefinedType get_type() const noexcept {
        return m_type;
    }

    const std::string& get_name() const noexcept {
        return m_name;
    }

    bool is_multiple() const noexcept {
        return m_multiple;
    }

    bool is_tuple() const noexcept {
        return m_tuple;
    }

    const std::optional<tuple_element_t> get_counter() const noexcept {
        return m_counter;
    }

    const std::vector<tuple_element_t>& get_tuple_elements() const noexcept {
        return m_tuple_elements;
    }

    const std::set<std::string>& get_enumerators() const noexcept {
        return m_enumerators;
    }

    friend bool            validate(const Parameter& p, const ANTLRToken* token, const AsamVariantType& value);
    friend AsamVariantType convert(const Parameter& p, std::string_view text);

   private:

    PredefinedType                 m_type;
    std::string                    m_name;
    bool                           m_multiple;
    bool                           m_tuple;
    std::set<std::string>          m_enumerators;
    std::optional<tuple_element_t> m_counter;
    std::vector<tuple_element_t>   m_tuple_elements{};
};

bool validate(const Parameter& p, const ANTLRToken* token, const AsamVariantType& value) {
    bool ok{ false };

    if (std::size(p.get_enumerators()) == 0) {
        const auto entry = ASAM_TYPES[std::bit_cast<std::uint16_t>(p.m_type) - 1];
        ok              = entry->validate(value);
		if (!ok) {
            spdlog::get("a2lparser")->warn("Value out of range [{}:{}]", token->line(), token->column());
			if (std::holds_alternative<unsigned long long>(value)) {
                spdlog::get("a2lparser")->warn("\t\tVALUE [unsigned long long]: {}", std::to_string(std::get<unsigned long long>(value)));
			} else if (std::holds_alternative<signed long long>(value)) {
                spdlog::get("a2lparser")->warn("\t\tVALUE [signed long long]: {}", std::to_string(std::get<signed long long>(value)));
			} else if (std::holds_alternative<long double>(value)) {
                spdlog::get("a2lparser")->warn("\t\tVALUE [long double]: {}", std::to_string(std::get<long double>(value)));
			} else if (std::holds_alternative<std::string>(value)) {
                spdlog::get("a2lparser")->warn("\t\tVALUE [string]: {}", std::get<std::string>(value));
			}
		}
        auto valid_type = entry->m_valid_tokens.contains(static_cast<A2LTokenType>(token->getType()));
        return ok && valid_type;
    } else {
        ok = p.get_enumerators().contains(std::get<std::string>(value));
        if (!ok) {
            spdlog::get("a2lparser")->error(
                "Enumeration '{} [{}:{}] must be one of: {} -- got: '{}'.", p.m_name, token->line(), token->column(),
                valid_enumerators(p.m_enumerators), std::get<std::string>(value));
        }
        return ok;
    }
}

AsamVariantType convert(PredefinedType type, std::string_view text) {
    switch (type) {
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
}

class ParameterTupleParser {
   public:

    enum class StateType : std::uint8_t {
        IDLE = 0,
        COLLECTING,
        EXCESS_TOKENS,
        FINISHED,
    };

    using table_t = std::vector<std::vector<AsamVariantType>>;

    explicit ParameterTupleParser(const Parameter& parameter) :
        m_parameter(parameter),
        m_tuple_elements(parameter.get_tuple_elements()),
        m_state(StateType::IDLE),
        m_idx(0),
        m_column(0),
        m_tuple_size(0),
        m_started(false),
        m_token_count(0) {
    }

    void feed(const ANTLRToken* token) noexcept {
        if (!m_started) {
            auto [tp, name]  = m_parameter.get_counter().value();
            auto converted_value = convert(tp, token->getText());
            unsigned long long tuple_count = 0ULL;
           if (std::holds_alternative<signed long long>(converted_value)) {
                tuple_count = static_cast<unsigned long long>(std::get<signed long long>(converted_value));
            } else if (std::holds_alternative<long double>(converted_value)) {
                tuple_count = static_cast<unsigned long long>(std::get<long double>(converted_value));
            } else if (std::holds_alternative<std::string>(converted_value)) {
                tuple_count =  std::strtoll(std::get<std::string>(converted_value).c_str(), nullptr, 10);
            }
            m_tuple_size     = std::size(m_parameter.get_tuple_elements());
            m_row.resize(m_tuple_size);
            m_token_count = tuple_count * m_tuple_size;
            m_started     = true;
            m_state       = StateType::COLLECTING;
        } else {
            auto type       = std::get<0>(m_tuple_elements[m_column]);
            m_row[m_column] = convert(type, token->getText());
            m_column++;
            if (m_column == m_tuple_size) {
                m_column = 0;
                m_rows.emplace_back(m_row);
            }
            m_idx++;
            if (m_idx >= m_token_count) {
                m_state = StateType::FINISHED;
            }
        }
    }

    StateType get_state() const noexcept {
        return m_state;
    }

    table_t get_table() const noexcept {
        return m_rows;
    }

   private:

    const Parameter&                               m_parameter;
    const std::vector<Parameter::tuple_element_t>& m_tuple_elements;
    StateType                                      m_state;
    std::size_t                                    m_idx;
    std::size_t                                    m_column;
    std::size_t                                    m_tuple_size;
    bool                                           m_started;
    std::size_t                                    m_token_count;
    std::vector<AsamVariantType>                   m_row;
    table_t                                        m_rows;
};

#endif  // __PARAMETER_HPP
