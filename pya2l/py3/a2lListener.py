# Generated from a2l.g4 by ANTLR 4.5.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .a2lParser import a2lParser
else:
    from a2lParser import a2lParser

# This class defines a complete listener for a parse tree produced by a2lParser.
class a2lListener(ParseTreeListener):

    # Enter a parse tree produced by a2lParser#a2lFile.
    def enterA2lFile(self, ctx:a2lParser.A2lFileContext):
        pass

    # Exit a parse tree produced by a2lParser#a2lFile.
    def exitA2lFile(self, ctx:a2lParser.A2lFileContext):
        pass


    # Enter a parse tree produced by a2lParser#version.
    def enterVersion(self, ctx:a2lParser.VersionContext):
        pass

    # Exit a parse tree produced by a2lParser#version.
    def exitVersion(self, ctx:a2lParser.VersionContext):
        pass


    # Enter a parse tree produced by a2lParser#block.
    def enterBlock(self, ctx:a2lParser.BlockContext):
        pass

    # Exit a parse tree produced by a2lParser#block.
    def exitBlock(self, ctx:a2lParser.BlockContext):
        pass


    # Enter a parse tree produced by a2lParser#valueIdent.
    def enterValueIdent(self, ctx:a2lParser.ValueIdentContext):
        pass

    # Exit a parse tree produced by a2lParser#valueIdent.
    def exitValueIdent(self, ctx:a2lParser.ValueIdentContext):
        pass


    # Enter a parse tree produced by a2lParser#valueString.
    def enterValueString(self, ctx:a2lParser.ValueStringContext):
        pass

    # Exit a parse tree produced by a2lParser#valueString.
    def exitValueString(self, ctx:a2lParser.ValueStringContext):
        pass


    # Enter a parse tree produced by a2lParser#valueInt.
    def enterValueInt(self, ctx:a2lParser.ValueIntContext):
        pass

    # Exit a parse tree produced by a2lParser#valueInt.
    def exitValueInt(self, ctx:a2lParser.ValueIntContext):
        pass


    # Enter a parse tree produced by a2lParser#valueHex.
    def enterValueHex(self, ctx:a2lParser.ValueHexContext):
        pass

    # Exit a parse tree produced by a2lParser#valueHex.
    def exitValueHex(self, ctx:a2lParser.ValueHexContext):
        pass


    # Enter a parse tree produced by a2lParser#valueFloat.
    def enterValueFloat(self, ctx:a2lParser.ValueFloatContext):
        pass

    # Exit a parse tree produced by a2lParser#valueFloat.
    def exitValueFloat(self, ctx:a2lParser.ValueFloatContext):
        pass


    # Enter a parse tree produced by a2lParser#valueBlock.
    def enterValueBlock(self, ctx:a2lParser.ValueBlockContext):
        pass

    # Exit a parse tree produced by a2lParser#valueBlock.
    def exitValueBlock(self, ctx:a2lParser.ValueBlockContext):
        pass


