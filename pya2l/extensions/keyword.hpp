
#if !defined __KEYWORD_HPP
    #define __KEYWORD_HPP

    #include "a2ltoken.hpp"
    #include "parameter.hpp"

class Keyword {
   public:

    using map_t = std::vector<Keyword>;

    Keyword(
        A2LTokenType token, std::string_view name, std::string_view class_name, bool block, bool multiple,
        const std::initializer_list<Parameter>& parameters, const map_t& keywords
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

#endif  // __KEYWORD_HPP
