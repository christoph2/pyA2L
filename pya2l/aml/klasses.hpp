
#if !defined(__KLASSES_HPP)
    #define __KLASSES_HPP

    #include <cstdint>
    #include <optional>
    #include <variant>

using string_opt_t = std::optional<std::string>;
using numeric_t    = std::variant<std::monostate, std::uint64_t, long double>;

class TaggedUnionMember {
   public:

    TaggedUnionMember() = delete;

    TaggedUnionMember(const string_opt_t& tag) : m_tag(tag) {
    }

   private:

    string_opt_t m_tag;
};

    #if 0
class TaggedUnionMember(BaseType):
    def __init__(self, tag, member, block_definition):
        self.tag = tag
        self.member = member
        self.block_definition = block_definition

    def __repr__(self):
        return "TaggedUnionMember(tag = {}, member = {}, block_definition = {})".format(
            self.tag, self.member, self.block_definition
        )
    #endif

#endif
