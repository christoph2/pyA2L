
#if !defined __VALUECONTAINER_HPP
    #define __VALUECONTAINER_HPP

const std::string as_string(const AsamVariantType& v) {
    std::ostringstream os;

    os << "Value(";
    if (std::holds_alternative<std::string>(v)) {
        os << std::get<std::string>(v);
    } else if (std::holds_alternative<unsigned long long>(v)) {
        os << std::to_string(std::get<unsigned long long>(v));
    } else if (std::holds_alternative<signed long long>(v)) {
        os << std::to_string(std::get<signed long long>(v));
    } else if (std::holds_alternative<long double>(v)) {
        os << std::to_string(std::get<long double>(v));
    }
    os << ")";

    return os.str();
}

class ValueContainer {
   public:

    using key_value_list_t = std::vector<AsamVariantType>;

    using container_type      = ValueContainer;
    using container_list_type = std::vector<container_type>;

    ~ValueContainer() noexcept = default;

    explicit ValueContainer(std::string_view name) : m_name(name), m_parameters(), m_keywords(), m_multiple_values() {
    }

    ValueContainer(const ValueContainer& other) noexcept            = default;
    ValueContainer& operator=(const ValueContainer& other) noexcept = delete;
    ValueContainer(ValueContainer&& other) noexcept                 = default;
    ValueContainer& operator=(ValueContainer&& other) noexcept      = default;

    void set_parameters(key_value_list_t&& parameters) noexcept {
        m_parameters = std::move(parameters);
    }

    void set_multiple_values(std::vector<AsamVariantType>&& multiple_values) noexcept {
        m_multiple_values = std::move(multiple_values);
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

    const auto& get_multiple_values() const noexcept {
        return m_multiple_values;
    }

    const std::string to_string() const {
        std::ostringstream os;

        os << "ValueContainer(name: '" << get_name() << "'";

        for (const auto& param : get_parameters()) {
            os << "\t: " << as_string(param) << "; " << std::endl;
        }

        for (const auto& kw : get_keywords()) {
            os << "\t: " << kw.to_string() << std::endl;
        }

        os << ");" << std::endl;
        return os.str();
    }

    static void set_encoding(std::string_view encoding) {
        s_encoding = encoding;
    }

    static const std::string& get_encoding() {
        return s_encoding;
    }

   private:

    std::string                  m_name;
    key_value_list_t             m_parameters;
    container_list_type          m_keywords;
    std::vector<AsamVariantType> m_multiple_values;

    static std::string s_encoding;
};

#endif  // __VALUECONTAINER_HPP
