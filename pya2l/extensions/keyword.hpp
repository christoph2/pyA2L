
#if !defined __KEYWORD_HPP
    #define __KEYWORD_HPP

    #include "a2ltoken.hpp"
    #include "parameter.hpp"

template<>
struct std::hash<A2LTokenType> {
    std::size_t operator()(const A2LTokenType &s) const noexcept {
        return std::hash<uint16_t>{}(static_cast<uint16_t>(s));
    }
};

class Keyword {
   public:

    using keyword_map_t = std::unordered_map<A2LTokenType, std::shared_ptr<Keyword>>;

    Keyword(
        A2LTokenType token, std::string_view name, std::string_view class_name, bool block, bool multiple,
        const std::initializer_list<Parameter> &parameters, const std::vector<Keyword> &keywords
    ) :
        m_token(token), m_name(name), m_class_name(class_name), m_block(block), m_multiple(multiple), m_parameters(parameters) {
        for (const auto &kw : keywords) {
            m_keywords.insert({ kw.m_token, std::make_shared<Keyword>(kw) });
        }
    }

    Keyword() = default;

    Keyword(const Keyword &other) :
        m_token(other.m_token),
        m_name(other.m_name),
        m_class_name(other.m_class_name),
        m_block(other.m_block),
        m_multiple(other.m_multiple),
        m_parameters(other.m_parameters),
        m_keywords(other.m_keywords) {
    }

    Keyword(Keyword &&)                 = default;
    Keyword &operator=(const Keyword &) = delete;
    Keyword &operator=(Keyword &&)      = default;

    virtual ~Keyword() {
    }

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
        return *(m_keywords.find(token)->second.get());
    }

    // private:

    A2LTokenType           m_token;
    std::string            m_name;
    std::string            m_class_name;
    bool                   m_block;
    bool                   m_multiple;
    std::vector<Parameter> m_parameters;
    keyword_map_t          m_keywords;
    // std::unordered_map<A2LTokenType, Keyword> m_keywords;
    // std::map<A2LTokenType, Keyword> m_keywords;
};

#endif  // __KEYWORD_HPP
