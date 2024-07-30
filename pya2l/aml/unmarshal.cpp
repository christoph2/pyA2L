
#include "unmarshal.hpp"

auto unmarshal(const std::stringstream& inbuf) -> Node {
    auto unm    = Unmarshaller(inbuf);
    auto result = unm.run();
    return result;
}
