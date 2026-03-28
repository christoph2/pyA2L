
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
        std::cerr << "[ERROR (pya2l.AMLParser)] Runtime error while parsing AML file '" << aml_file_name << "': " << re.what() << std::endl;
    } catch (const std::exception& ex) {
        std::cerr << "[ERROR (pya2l.AMLParser)] Exception while parsing AML file '" << aml_file_name << "': " << ex.what() << std::endl;
    } catch (...) {
        std::cerr << "[ERROR (pya2l.AMLParser)] Unknown error while parsing AML file '" << aml_file_name << "' - no further information available." << std::endl;
    }
    return result;
}
