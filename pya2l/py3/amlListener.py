# Generated from aml.g4 by ANTLR 4.5.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .amlParser import amlParser
else:
    from amlParser import amlParser

# This class defines a complete listener for a parse tree produced by amlParser.
class amlListener(ParseTreeListener):

    # Enter a parse tree produced by amlParser#amlFile.
    def enterAmlFile(self, ctx:amlParser.AmlFileContext):
        pass

    # Exit a parse tree produced by amlParser#amlFile.
    def exitAmlFile(self, ctx:amlParser.AmlFileContext):
        pass


    # Enter a parse tree produced by amlParser#declaration.
    def enterDeclaration(self, ctx:amlParser.DeclarationContext):
        pass

    # Exit a parse tree produced by amlParser#declaration.
    def exitDeclaration(self, ctx:amlParser.DeclarationContext):
        pass


    # Enter a parse tree produced by amlParser#type_definition.
    def enterType_definition(self, ctx:amlParser.Type_definitionContext):
        pass

    # Exit a parse tree produced by amlParser#type_definition.
    def exitType_definition(self, ctx:amlParser.Type_definitionContext):
        pass


    # Enter a parse tree produced by amlParser#type_name.
    def enterType_name(self, ctx:amlParser.Type_nameContext):
        pass

    # Exit a parse tree produced by amlParser#type_name.
    def exitType_name(self, ctx:amlParser.Type_nameContext):
        pass


    # Enter a parse tree produced by amlParser#predefined_type_name.
    def enterPredefined_type_name(self, ctx:amlParser.Predefined_type_nameContext):
        pass

    # Exit a parse tree produced by amlParser#predefined_type_name.
    def exitPredefined_type_name(self, ctx:amlParser.Predefined_type_nameContext):
        pass


    # Enter a parse tree produced by amlParser#block_definition.
    def enterBlock_definition(self, ctx:amlParser.Block_definitionContext):
        pass

    # Exit a parse tree produced by amlParser#block_definition.
    def exitBlock_definition(self, ctx:amlParser.Block_definitionContext):
        pass


    # Enter a parse tree produced by amlParser#enum_type_name.
    def enterEnum_type_name(self, ctx:amlParser.Enum_type_nameContext):
        pass

    # Exit a parse tree produced by amlParser#enum_type_name.
    def exitEnum_type_name(self, ctx:amlParser.Enum_type_nameContext):
        pass


    # Enter a parse tree produced by amlParser#enumerator_list.
    def enterEnumerator_list(self, ctx:amlParser.Enumerator_listContext):
        pass

    # Exit a parse tree produced by amlParser#enumerator_list.
    def exitEnumerator_list(self, ctx:amlParser.Enumerator_listContext):
        pass


    # Enter a parse tree produced by amlParser#enumerator.
    def enterEnumerator(self, ctx:amlParser.EnumeratorContext):
        pass

    # Exit a parse tree produced by amlParser#enumerator.
    def exitEnumerator(self, ctx:amlParser.EnumeratorContext):
        pass


    # Enter a parse tree produced by amlParser#struct_type_name.
    def enterStruct_type_name(self, ctx:amlParser.Struct_type_nameContext):
        pass

    # Exit a parse tree produced by amlParser#struct_type_name.
    def exitStruct_type_name(self, ctx:amlParser.Struct_type_nameContext):
        pass


    # Enter a parse tree produced by amlParser#struct_member.
    def enterStruct_member(self, ctx:amlParser.Struct_memberContext):
        pass

    # Exit a parse tree produced by amlParser#struct_member.
    def exitStruct_member(self, ctx:amlParser.Struct_memberContext):
        pass


    # Enter a parse tree produced by amlParser#member.
    def enterMember(self, ctx:amlParser.MemberContext):
        pass

    # Exit a parse tree produced by amlParser#member.
    def exitMember(self, ctx:amlParser.MemberContext):
        pass


    # Enter a parse tree produced by amlParser#array_specifier.
    def enterArray_specifier(self, ctx:amlParser.Array_specifierContext):
        pass

    # Exit a parse tree produced by amlParser#array_specifier.
    def exitArray_specifier(self, ctx:amlParser.Array_specifierContext):
        pass


    # Enter a parse tree produced by amlParser#taggedstruct_type_name.
    def enterTaggedstruct_type_name(self, ctx:amlParser.Taggedstruct_type_nameContext):
        pass

    # Exit a parse tree produced by amlParser#taggedstruct_type_name.
    def exitTaggedstruct_type_name(self, ctx:amlParser.Taggedstruct_type_nameContext):
        pass


    # Enter a parse tree produced by amlParser#taggedstruct_member.
    def enterTaggedstruct_member(self, ctx:amlParser.Taggedstruct_memberContext):
        pass

    # Exit a parse tree produced by amlParser#taggedstruct_member.
    def exitTaggedstruct_member(self, ctx:amlParser.Taggedstruct_memberContext):
        pass


    # Enter a parse tree produced by amlParser#taggedstruct_definition.
    def enterTaggedstruct_definition(self, ctx:amlParser.Taggedstruct_definitionContext):
        pass

    # Exit a parse tree produced by amlParser#taggedstruct_definition.
    def exitTaggedstruct_definition(self, ctx:amlParser.Taggedstruct_definitionContext):
        pass


    # Enter a parse tree produced by amlParser#taggedunion_type_name.
    def enterTaggedunion_type_name(self, ctx:amlParser.Taggedunion_type_nameContext):
        pass

    # Exit a parse tree produced by amlParser#taggedunion_type_name.
    def exitTaggedunion_type_name(self, ctx:amlParser.Taggedunion_type_nameContext):
        pass


    # Enter a parse tree produced by amlParser#tagged_union_member.
    def enterTagged_union_member(self, ctx:amlParser.Tagged_union_memberContext):
        pass

    # Exit a parse tree produced by amlParser#tagged_union_member.
    def exitTagged_union_member(self, ctx:amlParser.Tagged_union_memberContext):
        pass


    # Enter a parse tree produced by amlParser#constant.
    def enterConstant(self, ctx:amlParser.ConstantContext):
        pass

    # Exit a parse tree produced by amlParser#constant.
    def exitConstant(self, ctx:amlParser.ConstantContext):
        pass


