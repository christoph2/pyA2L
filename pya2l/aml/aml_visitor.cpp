

#include "aml_visitor.h"

#include <iostream>

////// utils ///////////////

// Taken from Stackoverflow: https://stackoverflow.com/questions/216823/how-to-trim-a-stdstring

#include <algorithm>
#include <cctype>
#include <locale>

// trim from start (in place)
inline void ltrim(std::string &s) {
    s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](unsigned char ch) { return !std::isspace(ch); }));
}

// trim from end (in place)
inline void rtrim(std::string &s) {
    s.erase(std::find_if(s.rbegin(), s.rend(), [](unsigned char ch) { return !std::isspace(ch); }).base(), s.end());
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
std::string strip(std::string str, char chr = '"') {
    str.erase(0, str.find_first_not_of(chr));
    str.erase(str.find_last_not_of(chr) + 1);

    return str;
}

std::any AmlVisitor::visitAmlFile(amlParser::AmlFileContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitDeclaration(amlParser::DeclarationContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitType_definition(amlParser::Type_definitionContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitType_name(amlParser::Type_nameContext *ctx) {
    auto         ctx_t  = ctx->t;
    auto         ctx_pr = ctx->pr;
    auto         ctx_dt = ctx->st;
    auto         ctx_ts = ctx->ts;
    auto         ctx_tu = ctx->tu;
    auto         ctx_en = ctx->en;
    string_opt_t tag;
    string_opt_t pdt_name;
#if 0
   t = tagValue? (
     pr = predefined_type_name
   | st = struct_type_name
   | ts = taggedstruct_type_name
   | tu = taggedunion_type_name
   | en = enum_type_name
   )
#endif

#if 0
    if (ctx_t) {
        tag = std::any_cast<string_opt_t>(visit(ctx_t));
        std::cout << "\t\tType-tag: " << *tag << std::endl;
    }
    if (ctx_pr) {
        pdt_name = std::any_cast<string_opt_t>(visit(ctx_pr));
        std::cout << "\t\tType-PDT: " << *pdt_name << std::endl;
    }
    #endif
    if (ctx_dt) {
    }
    if (ctx_ts) {
    }
    if (ctx_tu) {
    }
    if (ctx_en) {
    }

    return visitChildren(ctx);
}

std::any AmlVisitor::visitPredefined_type_name(amlParser::Predefined_type_nameContext *ctx) {
    auto name = ctx->name->getText();

    std::cout << "\t\tPDTname: " << name << std::endl;

    //return name;
    return visitChildren(ctx);
}

std::any AmlVisitor::visitBlock_definition(amlParser::Block_definitionContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitEnum_type_name(amlParser::Enum_type_nameContext *ctx) {
    auto ctx_t0 = ctx->t0;
    auto ctx_t1 = ctx->t1;
    auto ctx_l  = ctx->l;
    bool is_referrer=false;
    string_opt_t tag0;
    string_opt_t tag1;

    if (ctx_t0) {
        auto tag0 = std::any_cast<string_opt_t>(ctx_t0);
        if (tag0) {
            std::cout << "\tEnum-Type: " << *tag0 << std::endl;
        }
    }

    if (ctx_t1) {
        auto tag1 = std::any_cast<string_opt_t>(ctx_t1);
        is_referrer = true;
        if (tag1) {
            std::cout << "\trefering Enum: " << *tag1 << std::endl;
        }
    }


#if 0
enum_type_name:
      ('enum' t0 = identifierValue? '{' l = enumerator_list '}' )
    | ('enum' t1 = identifierValue)
    ;
#endif
    return visitChildren(ctx);
}

std::any AmlVisitor::visitEnumerator_list(amlParser::Enumerator_listContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitEnumerator(amlParser::EnumeratorContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitStruct_type_name(amlParser::Struct_type_nameContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitStruct_member(amlParser::Struct_memberContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitMember(amlParser::MemberContext *ctx) {
    auto                   ctx_t = ctx->t;
    auto                   ctx_a = ctx->a;
    //std:: string           type_name;
    std::vector<numeric_t> arrary_specifier;

    if (ctx_t) {
        auto type_name = visit(ctx_t);
        if (type_name.has_value()) {
            auto xtt = std::any_cast<string_opt_t>(type_name);
            if (xtt) {
                std::cout << "\t\ttype_name: " << *xtt << std::endl;
            }
        }
    }

#if 0
    for (auto &&elem : ctx_a) {
        arrary_specifier.emplace_back(std::any_cast<numeric_t>(elem));
    }
#endif
    return visitChildren(ctx);
}

std::any AmlVisitor::visitArray_specifier(amlParser::Array_specifierContext *ctx) {
    auto array_spec = std::any_cast<numeric_t>(visit(ctx->c));  // numeric_t

    std::cout << "\t\tarray_spec" << std::endl;

    return array_spec;
}

std::any AmlVisitor::visitTaggedstruct_type_name(amlParser::Taggedstruct_type_nameContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitTaggedstruct_member(amlParser::Taggedstruct_memberContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitTaggedstruct_definition(amlParser::Taggedstruct_definitionContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitTaggedunion_type_name(amlParser::Taggedunion_type_nameContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitTagged_union_member(amlParser::Tagged_union_memberContext *ctx) {
    // auto tag = visit(ctx->t);
    auto ctx_t = ctx->t;
    auto ctx_m = ctx->m;
    auto ctx_b = ctx->b;

    std::cout << "\ttagged_union_member\n";

    if (ctx_t) {
        auto tag = std::any_cast<string_opt_t>(visit(ctx_t));
        std::cout << "\t\ttag: " << *tag << std::endl;
    } else {
    }

    if (ctx_m) {
        auto member = visit(ctx_m);
    } else {
    }

    if (ctx_b) {
        auto block_definition = visit(ctx_b);
    } else {
    }

    // return TaggedUnionMember(tag);

    return visitChildren(ctx);
}

std::any AmlVisitor::visitNumericValue(amlParser::NumericValueContext *ctx) {
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

std::any AmlVisitor::visitStringValue(amlParser::StringValueContext *ctx) {
    auto         ctx_s = ctx->s;
    string_opt_t result{ std::nullopt };

    if (ctx_s) {
        auto text = strip(trim_copy(ctx_s->getText()));

        std::cout << "STR: " << text << std::endl;
        result = text;
    }

    return result;
}

std::any AmlVisitor::visitTagValue(amlParser::TagValueContext *ctx) {
    auto         ctx_s = ctx->s;
    string_opt_t result{ std::nullopt };

    if (ctx_s) {
        auto text = strip(trim_copy(ctx_s->getText()));

        std::cout << "TAG: " << text << std::endl;
        result = text;
    }

    return result;
}

std::any AmlVisitor::visitIdentifierValue(amlParser::IdentifierValueContext *ctx) {
    auto         ctx_i = ctx->i;
    string_opt_t result{ std::nullopt };

    if (ctx_i) {
        auto text = strip(trim_copy(ctx_i->getText()));

        std::cout << "ID: " << text << std::endl;
        result = text;
    }

    return result;
}
