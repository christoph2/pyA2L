

#include "aml_visitor.h"

#include <iostream>

#include "klasses.hpp"

struct TypeRegistry {

    ~TypeRegistry() {
        for (auto& elem : m_registry) {
            delete elem;
        }
    }


    void add(Type * entry) {
        m_registry.push_back(entry);

    }

    std::vector<Type*> m_registry{};
};

static TypeRegistry type_registry;

template<typename Ty>
Type* make_type(const Ty& value) {
    auto result = new Type(value);
    type_registry.add(result);
    return result;
}


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
    auto ctx_d = ctx->d;

    for (auto& elem_ctx : ctx_d) {
        auto elem = visit(elem_ctx);
    }

    return visitChildren(ctx);
}

std::any AmlVisitor::visitDeclaration(amlParser::DeclarationContext *ctx) {
	auto ctx_t = ctx->t;
	auto ctx_b = ctx->b;

	if (ctx_t) {
		auto tp = visit(ctx_t);
	}

	if (ctx_b) {
		auto block = visit(ctx_b);
	}

    return visitChildren(ctx);
}

std::any AmlVisitor::visitType_definition(amlParser::Type_definitionContext *ctx) {
    auto td_ctx = ctx->type_name();

    if (td_ctx) {
        auto tn = visit(td_ctx);
        auto name = tn.type().name();
    }

    return visitChildren(ctx);
}

std::any AmlVisitor::visitType_name(amlParser::Type_nameContext *ctx) {
    auto         ctx_t  = ctx->t;
    auto         ctx_pr = ctx->pr;
    auto         ctx_st = ctx->st;
    auto         ctx_ts = ctx->ts;
    auto         ctx_tu = ctx->tu;
    auto         ctx_en = ctx->en;
    std::string pdt_name;
	std::string  tag_text{};

    if (ctx_t) {
       auto tag_opt = std::any_cast<string_opt_t>(visit(ctx_t));
       if (tag_opt) {
		  tag_text = *tag_opt;
          std::cout << "\t\tType-tag: " << tag_text << std::endl;
       }
    }
    if (ctx_pr) {
        pdt_name = std::any_cast<std::string>(visit(ctx_pr));
        return make_type(pdt_name);
        //std::cout << "\t\tType-PDT: " << pdt_name << std::endl;
    }
    if (ctx_st) {
        auto sst = std::any_cast<Struct>(visit(ctx_st));
        return make_type(sst);
    }
    if (ctx_ts) {
    }
    if (ctx_tu) {
    }
    if (ctx_en) {
        auto enumeration = std::any_cast<EnumerationOrReferrer>(visit(ctx_en));
    }

    return visitChildren(ctx);
    //return Type();
}

std::any AmlVisitor::visitPredefined_type_name(amlParser::Predefined_type_nameContext *ctx) {
    std::string name = ctx->name->getText();

    std::cout << "\t\tPDTname: " << name << std::endl;

    return name;
}

std::any AmlVisitor::visitBlock_definition(amlParser::Block_definitionContext *ctx) {
	auto ctx_tag  = ctx->tag;
	auto ctx_tn = ctx->tn;
	auto ctx_mem = ctx->mem;
	auto ctx_mult = ctx->mult;

	std::string tag_text;
    bool multiple{ false };

	if (ctx_tag) {
        auto tag_opt = std::any_cast<string_opt_t>(visit(ctx_tag));
        if (tag_opt) {
            tag_text = *tag_opt;
        }
    }

    if (ctx_mem) {
        auto mem = visit(ctx_mem);
    }

    if (ctx_mult) {
        if (ctx_mult->getText() == "*") {
            multiple = true;
        }
    }

	return visitChildren(ctx);
}

std::any AmlVisitor::visitEnum_type_name(amlParser::Enum_type_nameContext *ctx) {
    auto                    ctx_t0      = ctx->t0;
    auto                    ctx_t1      = ctx->t1;
    auto                    ctx_l       = ctx->l;
    bool                    is_referrer = false;
    std::string             name;
    std::string 			ref_name;
    std::vector<Enumerator> enumerators;
    EnumerationOrReferrer   result;


    if (ctx_t0) {
        auto str_opt = std::any_cast<string_opt_t>(visit(ctx_t0));
        if (str_opt) {
            //std::cout << "\tEnum-Type: " << *str_opt << std::endl;
            name = *str_opt;
        }
    }

    if (ctx_t1) {
        auto str_opt     = std::any_cast<string_opt_t>(visit(ctx_t1));
        is_referrer = true;
        if (str_opt) {
            //std::cout << "\trefering Enum: " << *str_opt << std::endl;
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
    auto                    enumerators = ctx->ids;

    for (auto &&en : enumerators) {
        result.emplace_back(std::any_cast<Enumerator>(visit(en)));
    }
    return result;
}

std::any AmlVisitor::visitEnumerator(amlParser::EnumeratorContext *ctx) {
    auto                     ctx_t = ctx->t;
    auto                     ctx_c = ctx->c;
    string_opt_t             tag;
    std::string              text{};
    std::optional<numeric_t> value{ std::nullopt };

    if (ctx_t) {
        tag = std::any_cast<string_opt_t>(visit(ctx_t));
        //std::cout << "\t\t\tenumerator-tag: " << *tag << std::endl;
        text = *tag;
    } else {
        //std::cout << "\t\t\tenumerator-tag: (NONE)" << std::endl;
    }
    if (ctx_c) {
        value = std::any_cast<numeric_t>(visit(ctx_c));
        if (value) {
            //std::cout << "\t\t\tenumerator-value: " << as_double(*value) << std::endl;
        }
    }

    return Enumerator(text, value);
}

std::any AmlVisitor::visitStruct_type_name(amlParser::Struct_type_nameContext *ctx) {
    auto ctx_t0 = ctx->t0;
    auto ctx_t1 = ctx->t1;
    auto ctx_l = ctx->l;
	bool is_referrer{false};
    std::string             name;
    std::string 			ref_name;
    std::vector<StructMember> members;
    StructOrReferrer   result;


    if (ctx_t0) {
        auto str_opt = std::any_cast<string_opt_t>(visit(ctx_t0));
        if (str_opt) {
            std::cout << "\tStruct-Type: " << *str_opt << std::endl;
            name = *str_opt;
        }
    }

    if (ctx_t1) {
        auto str_opt     = std::any_cast<string_opt_t>(visit(ctx_t1));
        is_referrer = true;
        if (str_opt) {
            std::cout << "\trefering Struct: " << *str_opt << std::endl;
            ref_name = *str_opt;
        }
    }

    for (auto& mem_ctx : ctx_l) {
        auto mem = visit(mem_ctx);

    }

    if (is_referrer) {
        result = Referrer(ReferrerType::StructType, ref_name);
    }
    else {
        result = Struct(name, members);
    }

    return result;
    //return visitChildren(ctx);
}

std::any AmlVisitor::visitStruct_member(amlParser::Struct_memberContext *ctx) {
	auto ctx_m = ctx->m;
	auto ctx_mstar = ctx->mstar;
	auto ctx_m0 = ctx->m0;
    bool multiple{ false };

	if (ctx_m) {
		auto value_opt = visit(ctx_m);
        auto mem = std::any_cast<Member>(value_opt);
	}

	if (ctx_m0) {
        if (ctx_m0->getText() == "*") {
            multiple = true;
			if (ctx_mstar) {
                auto mem = visit(ctx_mstar);
			}
        }
	}

    return visitChildren(ctx);
}

std::any AmlVisitor::visitMember(amlParser::MemberContext *ctx) {
    auto                  ctx_t = ctx->t;
    auto                  ctx_a = ctx->a;
    std::vector<uint64_t> arrary_specifier;
    std::uint64_t         value;
    Type* tp = nullptr;

    if (ctx_t) {
        auto type_name = visit(ctx_t);
        if (type_name.has_value()) {
            tp = std::any_cast<Type*>(type_name);
            //if (xtt) {
            //    std::cout << "\t\ttype_name: " << *xtt << std::endl;
            //}
        }
    }

    for (auto &elem : ctx_a) {
        auto value_cont = std::any_cast<numeric_t>(visit(elem));

        if (std::holds_alternative<std::uint64_t>(value_cont)) {
            value = std::get<std::uint64_t>(value_cont);
        } else if (std::holds_alternative<long double>(value_cont)) {
            value = std::bit_cast<std::uint64_t>(std::get<long double>(value_cont));
        }

        std::cout << "\t\t\tarray_spec: " << value
                  << std::endl;  // std::variant<struct std::monostate,unsigned __int64,long double>
        arrary_specifier.push_back(value);
    }
    return Member(tp, arrary_specifier);
}

std::any AmlVisitor::visitArray_specifier(amlParser::Array_specifierContext *ctx) {
    auto array_spec = std::any_cast<numeric_t>(visit(ctx->c));

    return array_spec;
}

std::any AmlVisitor::visitTaggedstruct_type_name(amlParser::Taggedstruct_type_nameContext *ctx) {
    auto ctx_t0 = ctx->t0;
    auto ctx_t1 = ctx->t1;
    auto ctx_l = ctx->l;
	bool is_referrer{false};
    std::string             name;
    std::string 			ref_name;
    std::vector<TaggedStructMember> members;
    TaggedStructOrReferrer   result;

    if (ctx_t0) {
        auto str_opt = std::any_cast<string_opt_t>(visit(ctx_t0));
        if (str_opt) {
            std::cout << "\tTaggedStruct-Type: " << *str_opt << std::endl;
            name = *str_opt;
        }
    }

    if (ctx_t1) {
        auto str_opt     = std::any_cast<string_opt_t>(visit(ctx_t1));
        is_referrer = true;
        if (str_opt) {
            std::cout << "\trefering TaggedStruct: " << *str_opt << std::endl;
            ref_name = *str_opt;
        }
    }

    for (auto& mem_ctx : ctx_l) {
        auto mem = visit(mem_ctx);

    }
    return visitChildren(ctx);
}

std::any AmlVisitor::visitTaggedstruct_member(amlParser::Taggedstruct_memberContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitTaggedstruct_definition(amlParser::Taggedstruct_definitionContext *ctx) {
    return visitChildren(ctx);
}

std::any AmlVisitor::visitTaggedunion_type_name(amlParser::Taggedunion_type_nameContext *ctx) {
    auto ctx_t0 = ctx->t0;
    auto ctx_t1 = ctx->t1;
    auto ctx_l = ctx->l;
	bool is_referrer{false};
    std::string             name;
    std::string 			ref_name;
    std::vector<TaggedUnionMember> members;
    TaggedUnionOrReferrer   result;

    if (ctx_t0) {
        auto str_opt = std::any_cast<string_opt_t>(visit(ctx_t0));
        if (str_opt) {
            std::cout << "\tTaggedUnion-Type: " << *str_opt << std::endl;
            name = *str_opt;
        }
    }

    if (ctx_t1) {
        auto str_opt     = std::any_cast<string_opt_t>(visit(ctx_t1));
        is_referrer = true;
        if (str_opt) {
            std::cout << "\trefering UnionStruct: " << *str_opt << std::endl;
            ref_name = *str_opt;
        }
    }

    for (auto& mem_ctx : ctx_l) {
        auto mem = visit(mem_ctx);

    }
    return visitChildren(ctx);
}

std::any AmlVisitor::visitTagged_union_member(amlParser::Tagged_union_memberContext *ctx) {
    auto        ctx_t = ctx->t;
    auto        ctx_m = ctx->m;
    auto        ctx_b = ctx->b;
    std::string tag{};
    Member member;

    std::cout << "\ttagged_union_member\n";

    if (ctx_t) {
        auto tag_cont = std::any_cast<string_opt_t>(visit(ctx_t));
        if (tag_cont) {
            tag = *tag_cont;
        }
        std::cout << "\t\ttag: " << tag << std::endl;
    }
    if (ctx_m) {
        auto mmm = visit(ctx_m);
        //member = visit(ctx_m);
    }
    if (ctx_b) {
        auto block_definition = visit(ctx_b);
    }

    return TaggedUnionMember(tag, member, BlockDefinition());
}

std::any AmlVisitor::visitNumericValue(amlParser::NumericValueContext *ctx) {
    auto ctx_i = ctx->i;
    auto ctx_h = ctx->h;
    auto ctx_f = ctx->f;

    numeric_t result{};

    if (ctx_i) {
        auto text = ctx_i->getText();
        // std::cout << "INT: " << text << std::endl;
        result = std::strtoul(text.c_str(), nullptr, 10);
    } else if (ctx_h) {
        auto text = ctx_h->getText();
        // std::cout << "HEX: " << text << std::endl;
        result = std::strtoul(text.c_str() + 2, nullptr, 16);
    } else if (ctx_f) {
        auto text = ctx_f->getText();
        // std::cout << "FLOAT: " << text << std::endl;
        result = std::strtold(text.c_str(), nullptr);
    }

    return result;
}

std::any AmlVisitor::visitStringValue(amlParser::StringValueContext *ctx) {
    auto         ctx_s = ctx->s;
    string_opt_t result{ std::nullopt };

    if (ctx_s) {
        auto text = strip(trim_copy(ctx_s->getText()));

        // std::cout << "STR: " << text << std::endl;
        result = text;
    }

    return result;
}

std::any AmlVisitor::visitTagValue(amlParser::TagValueContext *ctx) {
    auto         ctx_s = ctx->s;
    string_opt_t result{ std::nullopt };

    if (ctx_s) {
        auto text = strip(trim_copy(ctx_s->getText()));

        // std::cout << "TAG: " << text << std::endl;
        result = text;
    }

    return result;
}

std::any AmlVisitor::visitIdentifierValue(amlParser::IdentifierValueContext *ctx) {
    auto         ctx_i = ctx->i;
    string_opt_t result{ std::nullopt };

    if (ctx_i) {
        auto text = strip(trim_copy(ctx_i->getText()));

        // std::cout << "ID: " << text << std::endl;
        result = text;
    }

    return result;
}
