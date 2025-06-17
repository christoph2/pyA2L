
#if !defined __ASAM_TYPES_HPP
    #define __ASAM_TYPES_HPP


using toke_type = std::size_t;

enum class PredefinedType : uint16_t {
    Int        = 1,
    Uint       = 2,
    Long       = 3,
    Ulong      = 4,
    Float      = 5,
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
};

struct AsamType {
    virtual ~AsamType()                                       = default;
    virtual bool validate(const AsamVariantType& value) const = 0;

    virtual std::string valid_range() const = 0;

    std::set<A2LTokenType> m_valid_tokens;
};

struct DummyEnum : public AsamType {
    bool validate(const AsamVariantType& value) const override {
        return true;
    }

    std::string valid_range() const override {
        return "";
    }
};

const std::string valid_enumerators(const std::set<std::string>& enumerators) {
    const auto  count = std::size(enumerators);
    std::size_t idx   = 0;
    std::string result;

    for (const auto& e : enumerators) {
        result.append('\'' + e + '\'');
        idx++;
        if (idx < count) {
            result.append(", ");
        }
    }
    return result;
}

struct Enum : public AsamType {
    using value_t = const std::set<std::string>;

    explicit Enum(std::string_view n, value_t&& e) : name{ n }, m_enumerators(std::move(e)) {
    }

    bool validate(const AsamVariantType& value) const override {
        const auto text_value = std::get<std::string>(value);
        return m_enumerators.contains(text_value.data());
    }

    std::string valid_range() const override {
        return valid_enumerators(m_enumerators);
    }

    std::string                 name;
    const std::set<std::string> m_enumerators{};
};

struct Ident : public AsamType {
    Ident() {
        m_valid_tokens = { A2LTokenType::IDENT };
    }

    bool validate(const AsamVariantType& value) const override {
        return true;
    }

    std::string valid_range() const override {
        return "";
    }
};

struct String : public AsamType {
    String() {
        m_valid_tokens = { A2LTokenType::STRING };
    }

    bool validate(const AsamVariantType& value) const override {
        return true;
    }

    std::string valid_range() const override {
        return "";
    }
};

template<typename Ty>
struct IntegralType : public AsamType {
    IntegralType() {
        m_valid_tokens = { A2LTokenType::INT, A2LTokenType::HEX };
    }

    bool validate(const AsamVariantType& value) const override {
        if constexpr (std::is_signed_v<Ty> == true) {
            const auto int_value = std::get<signed long long>(value);
            return (int_value < m_limits.min() || int_value > m_limits.max()) ? false : true;
        } else {
            const auto int_value = std::get<unsigned long long>(value);
            return (int_value < m_limits.min() || int_value > m_limits.max()) ? false : true;
        }
    }

    std::string valid_range() const override {
        return std::to_string(m_limits.min()) + ".." + std::to_string(m_limits.max());
    }

    std::numeric_limits<Ty> m_limits;
    const bool              is_signed = std::is_signed_v<Ty>;
};

struct Int : IntegralType<int16_t> {};

struct UInt : public IntegralType<uint16_t> {};

struct Long : public IntegralType<int32_t> {};

struct ULong : public IntegralType<uint32_t> {};

struct Float : public AsamType {
    Float() {
        m_valid_tokens = { A2LTokenType::FLOAT, A2LTokenType::INT, A2LTokenType::HEX };
    }

    bool validate(const AsamVariantType& value) const override {
        // auto fl_value = std::get<long double>(value);
        return true;
        // return (value < m_limits.min() || value > m_limits.max()) ? false : true;
    }

    long double tofloat(std::string_view text_value, uint8_t radix = 10) const {
        return std::strtold(text_value.data(), nullptr);
    }

    std::string valid_range() const override {
        return std::to_string(m_limits.min()) + ".." + std::to_string(m_limits.max());
    }

    std::numeric_limits<double> m_limits;
};

std::ostream& operator<<(std::ostream& os, const Enum& en) {
    std::string result;
    const auto  count = std::size(en.m_enumerators);
    std::size_t idx   = 0;

    for (const auto& e : en.m_enumerators) {
        result.append('"' + e + '"');
        idx++;
        if (idx < count) {
            result.append(", ");
        }
    }
    return os << result;
}

const auto asam_int    = Int();
const auto asam_uint   = UInt();
const auto asam_long   = Long();
const auto asam_ulong  = ULong();
const auto asam_float  = Float();
const auto asam_string = String();
const auto asam_enum   = DummyEnum();
const auto asam_ident  = Ident();

constexpr std::array<AsamType const * const, 14> ASAM_TYPES = {
    &asam_int, &asam_uint, &asam_long, &asam_ulong, &asam_float, &asam_string, &asam_enum, &asam_ident,
};

#endif  // __ASAM_TYPES_HPP
