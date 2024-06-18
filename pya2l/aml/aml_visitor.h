
#if !defined(__AML_VISITOR_H)
#define __AML_VISITOR_H


#include "amlParser.h"
#include "amlBaseVisitor.h"

#include "klasses.hpp"


class  AmlVisitor : public amlBaseVisitor {
public:

   std::any visitAmlFile(amlParser::AmlFileContext *ctx) override;

   std::any visitDeclaration(amlParser::DeclarationContext *ctx) override;

   std::any visitType_definition(amlParser::Type_definitionContext *ctx) override ;

   std::any visitType_name(amlParser::Type_nameContext *ctx) override;

   std::any visitPredefined_type_name(amlParser::Predefined_type_nameContext *ctx) override;

   std::any visitBlock_definition(amlParser::Block_definitionContext *ctx) override;

   std::any visitEnum_type_name(amlParser::Enum_type_nameContext *ctx) override;

   std::any visitEnumerator_list(amlParser::Enumerator_listContext *ctx) override;

   std::any visitEnumerator(amlParser::EnumeratorContext *ctx) override;

   std::any visitStruct_type_name(amlParser::Struct_type_nameContext *ctx) override;

   std::any visitStruct_member(amlParser::Struct_memberContext *ctx) override;

   std::any visitMember(amlParser::MemberContext *ctx) override;

   std::any visitArray_specifier(amlParser::Array_specifierContext *ctx) override;

   std::any visitTaggedstruct_type_name(amlParser::Taggedstruct_type_nameContext *ctx) override;

   std::any visitTaggedstruct_member(amlParser::Taggedstruct_memberContext *ctx) override;

   std::any visitTaggedstruct_definition(amlParser::Taggedstruct_definitionContext *ctx) override;

   std::any visitTaggedunion_type_name(amlParser::Taggedunion_type_nameContext *ctx) override;

   std::any visitTagged_union_member(amlParser::Tagged_union_memberContext *ctx) override;

   std::any visitNumericValue(amlParser::NumericValueContext *ctx) override;

   std::any visitStringValue(amlParser::StringValueContext *ctx) override;

   std::any visitTagValue(amlParser::TagValueContext *ctx) override;

   std::any visitIdentifierValue(amlParser::IdentifierValueContext *ctx) override;

};

#endif // __AML_VISITOR_H
