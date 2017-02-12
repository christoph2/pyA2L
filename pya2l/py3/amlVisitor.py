# Generated from aml.g4 by ANTLR 4.5.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .amlParser import amlParser
else:
    from amlParser import amlParser

# This class defines a complete generic visitor for a parse tree produced by amlParser.

class amlVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by amlParser#amlFile.
    def visitAmlFile(self, ctx:amlParser.AmlFileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#declaration.
    def visitDeclaration(self, ctx:amlParser.DeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#type_definition.
    def visitType_definition(self, ctx:amlParser.Type_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#type_name.
    def visitType_name(self, ctx:amlParser.Type_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#predefined_type_name.
    def visitPredefined_type_name(self, ctx:amlParser.Predefined_type_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#block_definition.
    def visitBlock_definition(self, ctx:amlParser.Block_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#enum_type_name.
    def visitEnum_type_name(self, ctx:amlParser.Enum_type_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#enumerator_list.
    def visitEnumerator_list(self, ctx:amlParser.Enumerator_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#enumerator.
    def visitEnumerator(self, ctx:amlParser.EnumeratorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#struct_type_name.
    def visitStruct_type_name(self, ctx:amlParser.Struct_type_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#struct_member.
    def visitStruct_member(self, ctx:amlParser.Struct_memberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#member.
    def visitMember(self, ctx:amlParser.MemberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#array_specifier.
    def visitArray_specifier(self, ctx:amlParser.Array_specifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#taggedstruct_type_name.
    def visitTaggedstruct_type_name(self, ctx:amlParser.Taggedstruct_type_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#taggedstruct_member.
    def visitTaggedstruct_member(self, ctx:amlParser.Taggedstruct_memberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#taggedstruct_definition.
    def visitTaggedstruct_definition(self, ctx:amlParser.Taggedstruct_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#taggedunion_type_name.
    def visitTaggedunion_type_name(self, ctx:amlParser.Taggedunion_type_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#tagged_union_member.
    def visitTagged_union_member(self, ctx:amlParser.Tagged_union_memberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#constant.
    def visitConstant(self, ctx:amlParser.ConstantContext):
        return self.visitChildren(ctx)



del amlParser