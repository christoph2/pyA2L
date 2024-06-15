

#include "aml_visitor.h"

#include <iostream>

#include <cstdint>
#include <variant>


////// utils ///////////////

// Taken from Stackoverflow: https://stackoverflow.com/questions/216823/how-to-trim-a-stdstring

#include <algorithm>
#include <cctype>
#include <locale>

// trim from start (in place)
inline void ltrim(std::string &s) {
    s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](unsigned char ch) {
        return !std::isspace(ch);
    }));
}

// trim from end (in place)
inline void rtrim(std::string &s) {
    s.erase(std::find_if(s.rbegin(), s.rend(), [](unsigned char ch) {
        return !std::isspace(ch);
    }).base(), s.end());
}
// trim from both ends (in place)
inline void trim(std::string &s) {
    rtrim(s);
    ltrim(s);
}

// trim from start (copying)
inline std::string ltrim_copy(std::string s) {
    ltrim(s);
    return s;
}

// trim from end (copying)
inline std::string rtrim_copy(std::string s) {
    rtrim(s);
    return s;
}

// trim from both ends (copying)
inline std::string trim_copy(std::string s) {
    trim(s);
    return s;
}
///////////////////////////


using string_opt_t = std::optional<std::string>;
using numeric_t = std::variant<std::monostate, std::uint64_t, long double>;


   std::any AmlVisitor::visitAmlFile(amlParser::AmlFileContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitDeclaration(amlParser::DeclarationContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitType_definition(amlParser::Type_definitionContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitType_name(amlParser::Type_nameContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitPredefined_type_name(amlParser::Predefined_type_nameContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitBlock_definition(amlParser::Block_definitionContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitEnum_type_name(amlParser::Enum_type_nameContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitEnumerator_list(amlParser::Enumerator_listContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitEnumerator(amlParser::EnumeratorContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitStruct_type_name(amlParser::Struct_type_nameContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitStruct_member(amlParser::Struct_memberContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitMember(amlParser::MemberContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitArray_specifier(amlParser::Array_specifierContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitTaggedstruct_type_name(amlParser::Taggedstruct_type_nameContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitTaggedstruct_member(amlParser::Taggedstruct_memberContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitTaggedstruct_definition(amlParser::Taggedstruct_definitionContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitTaggedunion_type_name(amlParser::Taggedunion_type_nameContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitTagged_union_member(amlParser::Tagged_union_memberContext *ctx)  {
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitNumericValue(amlParser::NumericValueContext *ctx)  {
    auto ctx_i = ctx->i;
    auto ctx_h = ctx->h;
    auto ctx_f = ctx->f;

    numeric_t result{};

    if (ctx_i) {
        auto text = ctx_i->getText();
        std::cout << "INT: " << text << std::endl;
        result = std::strtoul(text.c_str(), nullptr, 10);
    } else if (ctx_h) {
        auto text = ctx_h->getText();
        std::cout << "HEX: " << text << std::endl;
        result = std::strtoul(text.c_str() + 2, nullptr, 16);
    } else if (ctx_f) {
        auto text = ctx_f->getText();
        std::cout << "FLOAT: " << text << std::endl;
        result = std::strtold(text.c_str(), nullptr);
    }

    return result;
  }

   std::any AmlVisitor::visitStringValue(amlParser::StringValueContext *ctx)  {

    auto ctx_s = ctx->s;
    string_opt_t result{std::nullopt};

    if (ctx_s) {
        auto text = trim(ctx_s->getText());

        std::cout << "STR: " << text << ":" << std::replace(text.begin(), text.end(), '"', '');
        result = text;
    }

    return result;
  }

   std::any AmlVisitor::visitTagValue(amlParser::TagValueContext *ctx)  {
    //std::replace( s.begin(), s.end(), 'x', 'y');
    return visitChildren(ctx);
  }

   std::any AmlVisitor::visitIdentifierValue(amlParser::IdentifierValueContext *ctx)  {
    return visitChildren(ctx);
  }
