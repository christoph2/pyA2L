
#if !defined(__PARSER_HPP)
    #define __PARSER_HPP

    #include <string>

struct AmlData {
    std::string text;
    std::string parsed;

    const std::string get_text() const noexcept {
        return text;
    }

    const std::string get_parsed() const noexcept {
        return parsed;
    }
};

AmlData parse_aml(const std::string& aml_file_name);

#endif  // __PARSER_HPP
