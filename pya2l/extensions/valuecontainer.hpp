
#if !defined __VALUECONTAINER_HPP
    #define __VALUECONTAINER_HPP

class ValueContainer {
   public:

    //    using key_value_t      = std::tuple<std::string, std::variant<std::string, unsigned long long, long double>>;
    using key_value_t      = std::variant<std::string, unsigned long long, long double>;
    using key_value_list_t = std::vector< key_value_t>;

    using container_type      = ValueContainer;
    using container_list_type = std::vector<container_type>;

    ~ValueContainer() noexcept = default;

    explicit ValueContainer(std::string_view name) : m_name(name), m_parameters(), m_keywords() {
    }

    ValueContainer(const ValueContainer& other) noexcept            = default;
    ValueContainer& operator=(const ValueContainer& other) noexcept = delete;
    ValueContainer(ValueContainer&& other) noexcept                 = default;
    ValueContainer& operator=(ValueContainer&& other) noexcept      = default;

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

   private:

    std::string         m_name;
    key_value_list_t    m_parameters;
    container_list_type m_keywords;
};

#endif  // __VALUECONTAINER_HPP
