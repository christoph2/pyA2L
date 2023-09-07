
#if !defined __ASAM_TYPES_HPP
    #define __ASAM_TYPES_HPP

using toke_type = std::size_t;

enum class PredefinedType : std::uint16_t {
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
    virtual ~AsamType()                                 = default;
    virtual bool validate(std::string_view value) const = 0;

    virtual std::string valid_range() const = 0;

    std::set<A2LTokenType> m_valid_tokens;
};

struct DummyEnum : public AsamType {
    bool validate(std::string_view value) const override {
        return true;
    }

    std::string valid_range() const override {
        return "";
    }
};

struct Enum : public AsamType {
    using value_t = const std::set<std::string>;

    explicit Enum(std::string_view n, value_t e) : name{ n }, enumerators(std::move(e)) {
    }

    bool validate(std::string_view text_value) const override {
        return enumerators.contains(text_value.data());
    }

    std::string valid_range() const override {
        auto        idx   = 0;
        const auto  count = std::size(enumerators);
        std::string result;

        for (const auto& e : enumerators) {
            result.append('"' + e + '"');
            idx++;
            if (idx < count) {
                result.append(", ");
            }
        }
        return result;
    }

    std::string                 name;
    const std::set<std::string> enumerators{};
};

struct Ident : public AsamType {
    Ident() {
        m_valid_tokens = { A2LTokenType::IDENT };
    }

    bool validate(std::string_view text_value) const override {
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

    bool validate(std::string_view text_value) const override {
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

    bool validate(std::string_view text_value) const override {
        auto value = toint(text_value);
        return (value < m_limits.min() || value > m_limits.max()) ? false : true;
    }

    long long toint(std::string_view text_value, std::uint8_t radix = 10) const {
        return std::strtoll(text_value.data(), nullptr, radix);
    }

    std::string valid_range() const override {
        return std::to_string(m_limits.min()) + ".." + std::to_string(m_limits.max());
    }

    std::numeric_limits<Ty> m_limits;
};

struct Int : IntegralType<std::int16_t> {};

struct UInt : public IntegralType<std::uint16_t> {};

struct Long : public IntegralType<std::int32_t> {};

struct ULong : public IntegralType<std::uint32_t> {};

struct Float : public AsamType {
    Float() {
        m_valid_tokens = { A2LTokenType::FLOAT };
    }

    bool validate(std::string_view text_value) const override {
        auto value = tofloat(text_value);
        return true;
        // return (value < m_limits.min() || value > m_limits.max()) ? false : true;
    }

    long double tofloat(std::string_view text_value, std::uint8_t radix = 10) const {
        return std::strtold(text_value.data(), nullptr);
    }

    std::string valid_range() const override {
        return std::to_string(m_limits.min()) + ".." + std::to_string(m_limits.max());
    }

    std::numeric_limits<double> m_limits;
};

struct Datatype : public Enum {
    explicit Datatype() :
        Enum(
            "DATATYPE",
            {
                "UBYTE",
                "SBYTE",
                "UWORD",
                "SWORD",
                "ULONG",
                "SLONG",
                "A_UINT64",
                "A_INT64",
                "FLOAT16_IEEE",
                "FLOAT32_IEEE",
                "FLOAT64_IEEE",
            }
        ) {
    }
};

struct Indexorder : public Enum {
    explicit Indexorder() : Enum("INDEXORDER", { "INDEX_INCR", "INDEX_DECR" }) {
    }
};

struct Addrtype : public Enum {
    explicit Addrtype() : Enum("ADDTYPE", { "PBYTE", "PWORD", "PLONG", "DIRECT" }) {
    }
};

struct Byteorder : public Enum {
    explicit Byteorder() : Enum("BYTEORDER", { "LITTLE_ENDIAN", "BIG_ENDIAN", "MSB_LAST", "MSB_FIRST" }) {
    }
};

struct Datasize : public Enum {
    explicit Datasize() : Enum("DATASIZE", { "BYTE", "WORD", "LONG" }) {
    }
};

struct Linktype : public Enum {
    explicit Linktype() : Enum("LINKTYPE", { "SYMBOL_TYPE_LINK" }) {
    }
};

std::ostream& operator<<(std::ostream& os, const Enum& en) {
    std::string result;
    const auto  count = std::size(en.enumerators);
    std::size_t idx   = 0;

    for (const auto& e : en.enumerators) {
        result.append('"' + e + '"');
        idx++;
        if (idx < count) {
            result.append(", ");
        }
    }
    return os << result;
}

const auto asam_int        = Int();
const auto asam_uint       = UInt();
const auto asam_long       = Long();
const auto asam_ulong      = ULong();
const auto asam_float      = Float();
const auto asam_string     = String();
const auto asam_enum       = DummyEnum();
const auto asam_ident      = Ident();
const auto asam_datatype   = Datatype();
const auto asam_indexorder = Indexorder();
const auto asam_addrtype   = Addrtype();
const auto asam_byteorder  = Byteorder();
const auto asam_datasize   = Datasize();
const auto asam_link       = Linktype();

constexpr std::array<AsamType const * const, 14> SPRUNG_TABELLE = {
    &asam_int,   &asam_uint,     &asam_long,       &asam_ulong,    &asam_float,     &asam_string,   &asam_enum,
    &asam_ident, &asam_datatype, &asam_indexorder, &asam_addrtype, &asam_byteorder, &asam_datasize, &asam_link
};

#endif  // __ASAM_TYPES_HPP
