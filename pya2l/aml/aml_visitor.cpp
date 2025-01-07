

#include "aml_visitor.h"

#include <iostream>

#include "klasses.hpp"


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
    const auto ctx_d = ctx->d;

    std::vector<Declaration> decls;

    for (const auto &elem_ctx : ctx_d) {
        decls.emplace_back(std::any_cast<Declaration>(visit(elem_ctx)));
    }

    return AmlFile(decls);
}

std::any AmlVisitor::visitDeclaration(amlParser::DeclarationContext *ctx) {
    const auto      ctx_t = ctx->t;
    const auto      ctx_b = ctx->b;
    TypeDefinition  td;
    BlockDefinition block;

    if (ctx_t) {
        td = std::any_cast<TypeDefinition>(visit(ctx_t));
    }

    if (ctx_b) {
        block = std::any_cast<BlockDefinition>(visit(ctx_b));
    }

    return Declaration(td, block);
}

std::any AmlVisitor::visitType_definition(amlParser::Type_definitionContext *ctx) {
    const auto td_ctx = ctx->type_name();
    Type      *tp     = nullptr;

    if (td_ctx) {
        tp = std::any_cast<Type *>(visit(td_ctx));
    }

    return TypeDefinition(tp);
}

std::any AmlVisitor::visitType_name(amlParser::Type_nameContext *ctx) {
    const auto  ctx_pr = ctx->pr;
    const auto  ctx_st = ctx->st;
    const auto  ctx_ts = ctx->ts;
    const auto  ctx_tu = ctx->tu;
    const auto  ctx_en = ctx->en;

    if (ctx_pr) {
        auto pdt = std::any_cast<AMLPredefinedTypeEnum>(visit(ctx_pr));
        return make_type(pdt);
    }
    if (ctx_st) {
        const auto sst = std::any_cast<StructOrReferrer>(visit(ctx_st));
        return make_type(sst);
    }
    if (ctx_ts) {
        const auto sst = std::any_cast<TaggedStructOrReferrer>(visit(ctx_ts));
        return make_type(sst);
    }
    if (ctx_tu) {
        const auto sst = std::any_cast<TaggedUnionOrReferrer>(visit(ctx_tu));
        return make_type(sst);
    }
    if (ctx_en) {
        const auto enumeration = std::any_cast<EnumerationOrReferrer>(visit(ctx_en));
        return make_type(enumeration);
    }

    return {};
}

std::any AmlVisitor::visitPredefined_type_name(amlParser::Predefined_type_nameContext *ctx) {
    const std::string name = ctx->name->getText();

    return createPredefinedType(name);
}

std::any AmlVisitor::visitBlock_definition(amlParser::Block_definitionContext *ctx) {
    const auto ctx_tag  = ctx->tag;
    const auto ctx_tn   = ctx->tn;

    std::string tag_text;
    Type       *tn = nullptr;

    if (ctx_tag) {
        const auto tag_opt = std::any_cast<string_opt_t>(visit(ctx_tag));
        if (tag_opt) {
            tag_text = *tag_opt;
        }
    }

    if (ctx_tn) {
        tn = std::any_cast<Type *>(visit(ctx_tn));
    }

    return BlockDefinition(tag_text, tn/*, member, multiple*/);
}

std::any AmlVisitor::visitEnum_type_name(amlParser::Enum_type_nameContext *ctx) {
    const auto              ctx_t0      = ctx->t0;
    const auto              ctx_t1      = ctx->t1;
    const auto              ctx_l       = ctx->l;
    bool                    is_referrer = false;
    std::string             name;
    std::string             ref_name;
    std::vector<Enumerator> enumerators;
    EnumerationOrReferrer   result;

    if (ctx_t0) {
        const auto str_opt = std::any_cast<string_opt_t>(visit(ctx_t0));
        if (str_opt) {
            name = *str_opt;
        }
    }

    if (ctx_t1) {
        const auto str_opt = std::any_cast<string_opt_t>(visit(ctx_t1));
        is_referrer        = true;
        if (str_opt) {
            ref_name = *str_opt;
        }
    }

    if (ctx_l) {
        enumerators = std::any_cast<std::vector<Enumerator>>(visit(ctx_l));
    }

    if (is_referrer) {
        result = Referrer(ReferrerType::Enumeration, ref_name);
    } else {
        result = Enumeration(name, enumerators);
    }

    return result;
}

std::any AmlVisitor::visitEnumerator_list(amlParser::Enumerator_listContext *ctx) {
    std::vector<Enumerator> result{};

    for (const auto &en : ctx->ids) {
        result.emplace_back(std::any_cast<Enumerator>(visit(en)));
    }
    return result;
}

std::any AmlVisitor::visitEnumerator(amlParser::EnumeratorContext *ctx) {
    const auto               ctx_t = ctx->t;
    const auto               ctx_c = ctx->c;
    string_opt_t             tag;
    std::string              text{};
    std::optional<numeric_t> value{ std::nullopt };

    if (ctx_t) {
        tag  = std::any_cast<string_opt_t>(visit(ctx_t));
        text = *tag;
    }
    if (ctx_c) {
        value = std::any_cast<numeric_t>(visit(ctx_c));
    }

    return Enumerator(text, value);
}

std::any AmlVisitor::visitStruct_type_name(amlParser::Struct_type_nameContext *ctx) {
    const auto                ctx_t0 = ctx->t0;
    const auto                ctx_t1 = ctx->t1;
    const auto                ctx_l  = ctx->l;
    bool                      is_referrer{ false };
    std::string               name;
    std::string               ref_name;
    std::vector<StructMember> members;
    StructOrReferrer          result;

    if (ctx_t0) {
        const auto str_opt = std::any_cast<string_opt_t>(visit(ctx_t0));
        if (str_opt) {
            name = *str_opt;
        }
    }

    if (ctx_t1) {
        const auto str_opt = std::any_cast<string_opt_t>(visit(ctx_t1));
        is_referrer        = true;
        if (str_opt) {
            ref_name = *str_opt;
        }
    }

    for (const auto &mem_ctx : ctx_l) {
        const auto mem = std::any_cast<StructMember>(visit(mem_ctx));
        members.emplace_back(mem);
    }

    if (is_referrer) {
        result = Referrer(ReferrerType::StructType, ref_name);
    } else {
        result = Struct(name, members);
    }

    return result;
}

std::any AmlVisitor::visitStruct_member(amlParser::Struct_memberContext *ctx) {
    const auto ctx_m     = ctx->m;

    if (ctx_m) {
        const auto mem = std::any_cast<Member>(visit(ctx_m));
        return StructMember(mem);
    }

    return {};
}

std::any AmlVisitor::visitMember(amlParser::MemberContext *ctx) {
    const auto            ctx_t = ctx->t;
    const auto            ctx_a = ctx->a;
    const auto            ctx_b = ctx->b;
    std::vector<uint64_t> arrary_specifier{};
    std::int64_t          value{ 0 };
    Type                 *tp = nullptr;
    std::optional<BlockDefinition> block{std::nullopt};

    if (ctx_b) {
        block = std::any_cast<BlockDefinition>(visit(ctx_b));
    }
    else {

        if (ctx_t) {
            const auto type_name = visit(ctx_t);
            if (type_name.has_value()) {
                tp = std::any_cast<Type*>(type_name);
            }
        }

        for (const auto& elem : ctx_a) {
            const auto value_cont = std::any_cast<numeric_t>(visit(elem));

            if (std::holds_alternative<std::int64_t>(value_cont)) {
                value = std::get<std::int64_t>(value_cont);
            }
            else if (std::holds_alternative<long double>(value_cont)) {
                value = static_cast<std::int64_t>(std::get<long double>(value_cont));
            }
            arrary_specifier.push_back(value);
        }
    }
    return Member(block, tp, arrary_specifier);
}

std::any AmlVisitor::visitArray_specifier(amlParser::Array_specifierContext *ctx) {
    const auto array_spec = std::any_cast<numeric_t>(visit(ctx->c));

    return array_spec;
}

std::any AmlVisitor::visitTaggedstruct_type_name(amlParser::Taggedstruct_type_nameContext *ctx) {
    const auto                      ctx_t0 = ctx->t0;
    const auto                      ctx_t1 = ctx->t1;
    const auto                      ctx_l  = ctx->l;
    bool                            is_referrer{ false };
    std::string                     name;
    std::string                     ref_name;
    std::vector<TaggedStructMember> members;
    TaggedStructOrReferrer          result;

    if (ctx_t0) {
        const auto str_opt = std::any_cast<string_opt_t>(visit(ctx_t0));
        if (str_opt) {
            name = *str_opt;
        }
    }

    if (ctx_t1) {
        const auto str_opt = std::any_cast<string_opt_t>(visit(ctx_t1));
        is_referrer        = true;
        if (str_opt) {
            ref_name = *str_opt;
        }
    }

    for (const auto &mem_ctx : ctx_l) {
        const auto mem = std::any_cast<TaggedStructMember>(visit(mem_ctx));
        members.emplace_back(mem);
    }
    if (is_referrer) {
        result = Referrer(ReferrerType::TaggedStructType, ref_name);
    } else {
        result = TaggedStruct(name, members);
    }

    return result;
}

std::any AmlVisitor::visitTaggedstruct_member(amlParser::Taggedstruct_memberContext *ctx) {
    const auto ctx_ts0 = ctx->ts0;
    const auto ctx_ts1 = ctx->ts1;
    const auto ctx_bl0 = ctx->bl0;
    const auto ctx_bl1 = ctx->bl1;

    TaggedStructDefinition tsd;
    BlockDefinition        block;
    auto                   multiple{ false };

    if (ctx_ts0) {
        multiple = true;
        tsd      = std::any_cast<TaggedStructDefinition>(visit(ctx_ts0));
    } else if (ctx_ts1) {
        tsd = std::any_cast<TaggedStructDefinition>(visit(ctx_ts1));
    }

    if (ctx_bl0) {
        multiple = true;
        block    = std::any_cast<BlockDefinition>(visit(ctx_bl0));
    } else if (ctx_bl1) {
        block = std::any_cast<BlockDefinition>(visit(ctx_bl1));
    }

    return TaggedStructMember(tsd, block, multiple);
}

std::any AmlVisitor::visitTaggedstruct_definition(amlParser::Taggedstruct_definitionContext *ctx) {
    const auto length   = std::size(ctx->children);
    const auto multiple = (length > 4);
    const auto ctx_tag  = ctx->tag;
    const auto ctx_mem  = ctx->mem;

    std::string tag{};
    Member      member;

    if (ctx_tag) {
        const auto str_opt = std::any_cast<string_opt_t>(visit(ctx_tag));
        if (str_opt) {
            tag = *str_opt;
        }
    }

    if (ctx_mem) {
        member = std::any_cast<Member>(visit(ctx_mem));
    }

    return TaggedStructDefinition(tag, member, multiple);
}

std::any AmlVisitor::visitTaggedunion_type_name(amlParser::Taggedunion_type_nameContext *ctx) {
    const auto ctx_t0 = ctx->t0;
    const auto ctx_t1 = ctx->t1;
    const auto ctx_l  = ctx->l;

    bool                           is_referrer{ false };
    std::string                    name;
    std::string                    ref_name;
    std::vector<TaggedUnionMember> members;
    TaggedUnionOrReferrer          result;

    if (ctx_t0) {
        const auto str_opt = std::any_cast<string_opt_t>(visit(ctx_t0));
        if (str_opt) {
            name = *str_opt;
        }
    }

    if (ctx_t1) {
        const auto str_opt = std::any_cast<string_opt_t>(visit(ctx_t1));
        is_referrer        = true;
        if (str_opt) {
            ref_name = *str_opt;
        }
    }

    for (auto &mem_ctx : ctx_l) {
        const auto mem = std::any_cast<TaggedUnionMember>(visit(mem_ctx));
        members.emplace_back(mem);
    }
    if (is_referrer) {
        result = Referrer(ReferrerType::TaggedUnionType, ref_name);
    } else {
        result = TaggedUnion(name, members);
    }

    return result;
}

std::any AmlVisitor::visitTagged_union_member(amlParser::Tagged_union_memberContext *ctx) {
    const auto ctx_t = ctx->t;
    const auto ctx_m = ctx->m;
    const auto ctx_b = ctx->b;

    std::string     tag{};
    Member          member;
    BlockDefinition block;

    if (ctx_t) {
        const auto tag_cont = std::any_cast<string_opt_t>(visit(ctx_t));
        if (tag_cont) {
            tag = *tag_cont;
        }
    }
    if (ctx_m) {
        member = std::any_cast<Member>(visit(ctx_m));
    }
    if (ctx_b) {
        block = std::any_cast<BlockDefinition>(visit(ctx_b));
    }

    return TaggedUnionMember(tag, member, block);
}

std::any AmlVisitor::visitNumericValue(amlParser::NumericValueContext *ctx) {
    const auto ctx_i = ctx->i;
    const auto ctx_h = ctx->h;
    const auto ctx_f = ctx->f;

    numeric_t result{};

    if (ctx_i) {
        const auto text = ctx_i->getText();
        result          = std::strtoll(text.c_str(), nullptr, 10);
    } else if (ctx_h) {
        const auto text = ctx_h->getText();
        result          = std::strtoll(text.c_str() + 2, nullptr, 16);
    } else if (ctx_f) {
        const auto text = ctx_f->getText();
        result          = std::strtold(text.c_str(), nullptr);
    }

    return result;
}

std::any AmlVisitor::visitStringValue(amlParser::StringValueContext *ctx) {
    const auto   ctx_s = ctx->s;
    string_opt_t result{ std::nullopt };

    if (ctx_s) {
        const auto text = strip(trim_copy(ctx_s->getText()));
        result          = text;
    }

    return result;
}

std::any AmlVisitor::visitTagValue(amlParser::TagValueContext *ctx) {
    const auto   ctx_s = ctx->s;
    string_opt_t result{ std::nullopt };

    if (ctx_s) {
        const auto text = strip(trim_copy(ctx_s->getText()));
        result          = text;
    }

    return result;
}

std::any AmlVisitor::visitIdentifierValue(amlParser::IdentifierValueContext *ctx) {
    const auto   ctx_i = ctx->i;
    string_opt_t result{ std::nullopt };

    if (ctx_i) {
        const auto text = strip(trim_copy(ctx_i->getText()));
        result          = text;
    }

    return result;
}
