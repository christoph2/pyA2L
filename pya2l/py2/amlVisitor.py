# Generated from aml.g4 by ANTLR 4.5.1
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by amlParser.

class amlVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by amlParser#amlFile.
    def visitAmlFile(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#declaration.
    def visitDeclaration(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#type_definition.
    def visitType_definition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#type_name.
    def visitType_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#predefined_type_name.
    def visitPredefined_type_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#block_definition.
    def visitBlock_definition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#enum_type_name.
    def visitEnum_type_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#enumerator_list.
    def visitEnumerator_list(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#enumerator.
    def visitEnumerator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#struct_type_name.
    def visitStruct_type_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#struct_member.
    def visitStruct_member(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#member.
    def visitMember(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#array_specifier.
    def visitArray_specifier(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#taggedstruct_type_name.
    def visitTaggedstruct_type_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#taggedstruct_member.
    def visitTaggedstruct_member(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#taggedstruct_definition.
    def visitTaggedstruct_definition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#taggedunion_type_name.
    def visitTaggedunion_type_name(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#tagged_union_member.
    def visitTagged_union_member(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by amlParser#constant.
    def visitConstant(self, ctx):
        return self.visitChildren(ctx)


