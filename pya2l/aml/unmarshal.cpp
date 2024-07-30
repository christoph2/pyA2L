
#include "unmarshal.hpp"

auto unmarshal(const std::stringstream& inbuf) -> Root {
    auto unm    = Unmarshaller(inbuf);
    auto result = unm.run();
    return Root(result);
}
