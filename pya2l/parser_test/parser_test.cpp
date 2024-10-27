
#include "preprocessor.hpp"
#include "a2lparser.hpp"

#include <iostream>

std::string ValueContainer::s_encoding{ "latin1" };

int main(int argc, char** argv) {
	std::cout << "Hello!!!\n";
	bool cmd = false;
    auto FN{ "C:\\csProjects\\pyA2L\\examples\\03G906021KE_9970_501409_P447_HAXN_EDC16U34_3.41.a2l" };

    cmd = argc > 1;


	Preprocessor p{ "INFO" };

    if (cmd) {
        auto res    = p.process(argv[1], "UTF-8");
        auto reader = std::get<2>(res);
        p.finalize();
        reader.open();
    //    auto id = reader.get({ 2297, 9, 2307, 20 });
    //    reader.close();
    //    ld(p, 3);
    }

	return 0;
}
