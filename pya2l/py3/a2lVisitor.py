# Generated from a2l.g4 by ANTLR 4.5.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .a2lParser import a2lParser
else:
    from a2lParser import a2lParser

# This class defines a complete generic visitor for a parse tree produced by a2lParser.

class a2lVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by a2lParser#a2lFile.
    def visitA2lFile(self, ctx:a2lParser.A2lFileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by a2lParser#version.
    def visitVersion(self, ctx:a2lParser.VersionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by a2lParser#block.
    def visitBlock(self, ctx:a2lParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by a2lParser#valueIdent.
    def visitValueIdent(self, ctx:a2lParser.ValueIdentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by a2lParser#valueString.
    def visitValueString(self, ctx:a2lParser.ValueStringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by a2lParser#valueInt.
    def visitValueInt(self, ctx:a2lParser.ValueIntContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by a2lParser#valueHex.
    def visitValueHex(self, ctx:a2lParser.ValueHexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by a2lParser#valueFloat.
    def visitValueFloat(self, ctx:a2lParser.ValueFloatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by a2lParser#valueBlock.
    def visitValueBlock(self, ctx:a2lParser.ValueBlockContext):
        return self.visitChildren(ctx)



del a2lParser