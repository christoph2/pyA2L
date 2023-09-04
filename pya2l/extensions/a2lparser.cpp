
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
#include "token_stream.hpp"

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

    ValueContainer(std::string_view name) :
        m_name(name),
        m_parameters(){

        };

    void set_parameters(key_value_list_t&& parameters) {
        m_parameters = std::move(parameters);
    }

    ~ValueContainer() = default;

   private:

    std::string      m_name;
    key_value_list_t m_parameters;
};

#include "parser_table.hpp"

class Parser {
   public:

    explicit Parser(/*std::string_view*/ const std::string& file_name, Keyword& table) : m_reader("A2L.tmp"), m_table(table) {
        std::cout << "Parsing file: " << file_name << std::endl;
        m_kw_stack.push(m_table);
    }

    Parser(const Parser&) = delete;

    void parse() {
        auto idx = 0;

        auto root = ValueContainer("root");

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
                std::cout << "\t/END " << glied->getText() << "\n";
                assert(kw_tos().m_name == glied->getText());
                if (kw_tos().m_name == glied->getText()) {
                    m_kw_stack.pop();
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
                std::cout << idx++ << ": " << token->getText() << std::endl;
                const auto xxx = kw_tos().get(token->type());
                m_kw_stack.push(xxx);
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

            kw.set_parameters(do_parameters());

            if (kw_tos().m_block == false) {
                m_kw_stack.pop();
            }
            if (token_type() == A2LTokenType::END) {
                m_reader.consume();
                auto glied = m_reader.LT(1);
                std::cout << "\t/END " << glied->getText() << "\n";
                assert(kw_tos().m_name == glied->getText());
                if (kw_tos().m_name == glied->getText()) {
                    m_kw_stack.pop();
                }
                m_reader.consume();
            }
        }
    }

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
                        std::cout << "\t" << token->getText();
                        column++;
                        if (column == tuple_n) {
                            column = 0;
                            std::cout << std::endl;
                        }
                        idx++;
                        // if (idx >= token_count) {
                        //     break;
                        // }
                        m_reader.consume();
                    }
                } else {
                    std::cout << "\tParameter: " << parameter.m_name << R"( M? )" << parameter.m_multiple << std::endl;
                    std::cout << "\tValue: " << token->getText() << std::endl;

                    parameter_list.emplace_back(parameter.m_name, token->getText());

                    const auto expected = parameter.expected_token(token);
                    if ((parameter.m_multiple == true) && (!expected)) {
                        done = true;
                        continue;  // TODO: maybe break?
                    }
                    const auto valid = parameter.validate(token);
                    if (!expected) {
                        std::cout << "Unexpected token!!!\n";
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
        return m_value_stack.top();
    }

    A2LTokenType token_type(int k = 1) {
        return static_cast<A2LTokenType>(m_reader.LT(k)->getType());
    }

   private:

    TokenReader                m_reader;
    std::stack<Keyword>        m_kw_stack;
    std::stack<ValueContainer> m_value_stack;
    Keyword&                   m_table;
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

int main() {
    std::cout << asam_int.valid_range() << std::endl;
    std::cout << asam_uint.valid_range() << std::endl;

    const auto d = Datatype{};
    std::cout << d.valid_range() << std::endl;

    std::tuple<int, std::string, float> t1(10, "Test", 3.14);
    int                                 n  = 7;
    const auto                          t2 = std::tuple_cat(t1, std::make_tuple("Foo", "bar"), t1, std::tie(n));
    n                                      = 42;
    print(t2);

    auto parser = Parser("test.a2l", PARSER_TABLE);
    parser.parse();

    return 0;
}
