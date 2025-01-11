
#if !defined(__PARSER_HPP)
#define __PARSER_HPP


struct AmlData {
    std::string text;
    std::string parsed;
};

AmlData parse_aml(const std::string& aml_file_name);

#endif // __PARSER_HPP
