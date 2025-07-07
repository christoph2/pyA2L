
#include "parser.hpp"

#include <iostream>

#include "aml_lexer.hpp"
#include "aml_parser.hpp"
#include "unmarshal.hpp"

void marshal(std::stringstream& ss, const AmlFile& amlf);

AmlData parse_aml(const std::string& aml_file_name) {
    std::stringstream output;
    AmlData           result;

    try {
        auto file_content = get_file_content(aml_file_name);
        auto tokens       = aml_lexer(file_content);
        auto parser       = AMLParser{ tokens };
        auto amlf         = parser.parse();
        marshal(output, amlf);
        result.parsed = output.str();
        result.text   = file_content;
        // auto root_node = unmarshal(res);
    } catch (const std::runtime_error& re) {
        // speciffic handling for runtime_error
        std::cerr << "Error while parsing AML: " << re.what() << std::endl;
    } catch (const std::exception& ex) {
        // speciffic handling for all exceptions extending std::exception, except
        // std::runtime_error which is handled explicitly
        std::cerr << "Error while parsing AML: " << ex.what() << std::endl;
    } catch (...) {
        // catch any other errors (that we have no information about)
    }
    return result;
}
