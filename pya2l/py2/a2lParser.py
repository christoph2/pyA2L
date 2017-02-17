# Generated from a2l.g4 by ANTLR 4.5.1
# encoding: utf-8
from __future__ import print_function
from antlr4 import *
from io import StringIO

def serializedATN():
    with StringIO() as buf:
        buf.write(u"\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\3")
        buf.write(u"\r\'\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\3\2\5\2\f\n\2\3")
        buf.write(u"\2\3\2\3\3\3\3\3\3\3\3\3\4\3\4\3\4\7\4\27\n\4\f\4\16")
        buf.write(u"\4\32\13\4\3\4\3\4\3\4\3\5\3\5\3\5\3\5\3\5\3\5\5\5%\n")
        buf.write(u"\5\3\5\2\2\6\2\4\6\b\2\2)\2\13\3\2\2\2\4\17\3\2\2\2\6")
        buf.write(u"\23\3\2\2\2\b$\3\2\2\2\n\f\5\4\3\2\13\n\3\2\2\2\13\f")
        buf.write(u"\3\2\2\2\f\r\3\2\2\2\r\16\5\6\4\2\16\3\3\2\2\2\17\20")
        buf.write(u"\7\3\2\2\20\21\7\7\2\2\21\22\7\7\2\2\22\5\3\2\2\2\23")
        buf.write(u"\24\7\5\2\2\24\30\7\f\2\2\25\27\5\b\5\2\26\25\3\2\2\2")
        buf.write(u"\27\32\3\2\2\2\30\26\3\2\2\2\30\31\3\2\2\2\31\33\3\2")
        buf.write(u"\2\2\32\30\3\2\2\2\33\34\7\6\2\2\34\35\7\f\2\2\35\7\3")
        buf.write(u"\2\2\2\36%\7\f\2\2\37%\7\r\2\2 %\7\7\2\2!%\7\b\2\2\"")
        buf.write(u"%\7\t\2\2#%\5\6\4\2$\36\3\2\2\2$\37\3\2\2\2$ \3\2\2\2")
        buf.write(u"$!\3\2\2\2$\"\3\2\2\2$#\3\2\2\2%\t\3\2\2\2\5\13\30$")
        return buf.getvalue()


class a2lParser ( Parser ):

    grammarFileName = "a2l.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"'ASAP2_VERSION'", u"'/include'", u"'/begin'", 
                     u"'/end'" ]

    symbolicNames = [ u"<INVALID>", u"ASAP2_VERSION", u"INCLUDE", u"BEGIN", 
                      u"END", u"INT", u"HEX", u"FLOAT", u"COMMENT", u"WS", 
                      u"IDENT", u"STRING" ]

    RULE_a2lFile = 0
    RULE_version = 1
    RULE_block = 2
    RULE_value = 3

    ruleNames =  [ u"a2lFile", u"version", u"block", u"value" ]

    EOF = Token.EOF
    ASAP2_VERSION=1
    INCLUDE=2
    BEGIN=3
    END=4
    INT=5
    HEX=6
    FLOAT=7
    COMMENT=8
    WS=9
    IDENT=10
    STRING=11

    def __init__(self, input):
        super(a2lParser, self).__init__(input)
        self.checkVersion("4.5.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class A2lFileContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(a2lParser.A2lFileContext, self).__init__(parent, invokingState)
            self.parser = parser

        def block(self):
            return self.getTypedRuleContext(a2lParser.BlockContext,0)


        def version(self):
            return self.getTypedRuleContext(a2lParser.VersionContext,0)


        def getRuleIndex(self):
            return a2lParser.RULE_a2lFile

        def enterRule(self, listener):
            if hasattr(listener, "enterA2lFile"):
                listener.enterA2lFile(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitA2lFile"):
                listener.exitA2lFile(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitA2lFile"):
                return visitor.visitA2lFile(self)
            else:
                return visitor.visitChildren(self)




    def a2lFile(self):

        localctx = a2lParser.A2lFileContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_a2lFile)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 9
            _la = self._input.LA(1)
            if _la==a2lParser.ASAP2_VERSION:
                self.state = 8
                self.version()


            self.state = 11
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class VersionContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(a2lParser.VersionContext, self).__init__(parent, invokingState)
            self.parser = parser
            self.v0 = None # Token
            self.v1 = None # Token

        def ASAP2_VERSION(self):
            return self.getToken(a2lParser.ASAP2_VERSION, 0)

        def INT(self, i=None):
            if i is None:
                return self.getTokens(a2lParser.INT)
            else:
                return self.getToken(a2lParser.INT, i)

        def getRuleIndex(self):
            return a2lParser.RULE_version

        def enterRule(self, listener):
            if hasattr(listener, "enterVersion"):
                listener.enterVersion(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitVersion"):
                listener.exitVersion(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitVersion"):
                return visitor.visitVersion(self)
            else:
                return visitor.visitChildren(self)




    def version(self):

        localctx = a2lParser.VersionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_version)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 13
            self.match(a2lParser.ASAP2_VERSION)
            self.state = 14
            localctx.v0 = self.match(a2lParser.INT)
            self.state = 15
            localctx.v1 = self.match(a2lParser.INT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class BlockContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(a2lParser.BlockContext, self).__init__(parent, invokingState)
            self.parser = parser
            self.kw0 = None # Token
            self.kw1 = None # Token

        def BEGIN(self):
            return self.getToken(a2lParser.BEGIN, 0)

        def END(self):
            return self.getToken(a2lParser.END, 0)

        def IDENT(self, i=None):
            if i is None:
                return self.getTokens(a2lParser.IDENT)
            else:
                return self.getToken(a2lParser.IDENT, i)

        def value(self, i=None):
            if i is None:
                return self.getTypedRuleContexts(a2lParser.ValueContext)
            else:
                return self.getTypedRuleContext(a2lParser.ValueContext,i)


        def getRuleIndex(self):
            return a2lParser.RULE_block

        def enterRule(self, listener):
            if hasattr(listener, "enterBlock"):
                listener.enterBlock(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitBlock"):
                listener.exitBlock(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitBlock"):
                return visitor.visitBlock(self)
            else:
                return visitor.visitChildren(self)




    def block(self):

        localctx = a2lParser.BlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 17
            self.match(a2lParser.BEGIN)
            self.state = 18
            localctx.kw0 = self.match(a2lParser.IDENT)
            self.state = 22
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << a2lParser.BEGIN) | (1 << a2lParser.INT) | (1 << a2lParser.HEX) | (1 << a2lParser.FLOAT) | (1 << a2lParser.IDENT) | (1 << a2lParser.STRING))) != 0):
                self.state = 19
                self.value()
                self.state = 24
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 25
            self.match(a2lParser.END)
            self.state = 26
            localctx.kw1 = self.match(a2lParser.IDENT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ValueContext(ParserRuleContext):

        def __init__(self, parser, parent=None, invokingState=-1):
            super(a2lParser.ValueContext, self).__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return a2lParser.RULE_value

     
        def copyFrom(self, ctx):
            super(a2lParser.ValueContext, self).copyFrom(ctx)



    class ValueIdentContext(ValueContext):

        def __init__(self, parser, ctx): # actually a a2lParser.ValueContext)
            super(a2lParser.ValueIdentContext, self).__init__(parser)
            self.copyFrom(ctx)

        def IDENT(self):
            return self.getToken(a2lParser.IDENT, 0)

        def enterRule(self, listener):
            if hasattr(listener, "enterValueIdent"):
                listener.enterValueIdent(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitValueIdent"):
                listener.exitValueIdent(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitValueIdent"):
                return visitor.visitValueIdent(self)
            else:
                return visitor.visitChildren(self)


    class ValueBlockContext(ValueContext):

        def __init__(self, parser, ctx): # actually a a2lParser.ValueContext)
            super(a2lParser.ValueBlockContext, self).__init__(parser)
            self.copyFrom(ctx)

        def block(self):
            return self.getTypedRuleContext(a2lParser.BlockContext,0)


        def enterRule(self, listener):
            if hasattr(listener, "enterValueBlock"):
                listener.enterValueBlock(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitValueBlock"):
                listener.exitValueBlock(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitValueBlock"):
                return visitor.visitValueBlock(self)
            else:
                return visitor.visitChildren(self)


    class ValueStringContext(ValueContext):

        def __init__(self, parser, ctx): # actually a a2lParser.ValueContext)
            super(a2lParser.ValueStringContext, self).__init__(parser)
            self.copyFrom(ctx)

        def STRING(self):
            return self.getToken(a2lParser.STRING, 0)

        def enterRule(self, listener):
            if hasattr(listener, "enterValueString"):
                listener.enterValueString(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitValueString"):
                listener.exitValueString(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitValueString"):
                return visitor.visitValueString(self)
            else:
                return visitor.visitChildren(self)


    class ValueHexContext(ValueContext):

        def __init__(self, parser, ctx): # actually a a2lParser.ValueContext)
            super(a2lParser.ValueHexContext, self).__init__(parser)
            self.copyFrom(ctx)

        def HEX(self):
            return self.getToken(a2lParser.HEX, 0)

        def enterRule(self, listener):
            if hasattr(listener, "enterValueHex"):
                listener.enterValueHex(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitValueHex"):
                listener.exitValueHex(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitValueHex"):
                return visitor.visitValueHex(self)
            else:
                return visitor.visitChildren(self)


    class ValueIntContext(ValueContext):

        def __init__(self, parser, ctx): # actually a a2lParser.ValueContext)
            super(a2lParser.ValueIntContext, self).__init__(parser)
            self.copyFrom(ctx)

        def INT(self):
            return self.getToken(a2lParser.INT, 0)

        def enterRule(self, listener):
            if hasattr(listener, "enterValueInt"):
                listener.enterValueInt(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitValueInt"):
                listener.exitValueInt(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitValueInt"):
                return visitor.visitValueInt(self)
            else:
                return visitor.visitChildren(self)


    class ValueFloatContext(ValueContext):

        def __init__(self, parser, ctx): # actually a a2lParser.ValueContext)
            super(a2lParser.ValueFloatContext, self).__init__(parser)
            self.copyFrom(ctx)

        def FLOAT(self):
            return self.getToken(a2lParser.FLOAT, 0)

        def enterRule(self, listener):
            if hasattr(listener, "enterValueFloat"):
                listener.enterValueFloat(self)

        def exitRule(self, listener):
            if hasattr(listener, "exitValueFloat"):
                listener.exitValueFloat(self)

        def accept(self, visitor):
            if hasattr(visitor, "visitValueFloat"):
                return visitor.visitValueFloat(self)
            else:
                return visitor.visitChildren(self)



    def value(self):

        localctx = a2lParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_value)
        try:
            self.state = 34
            token = self._input.LA(1)
            if token in [a2lParser.IDENT]:
                localctx = a2lParser.ValueIdentContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 28
                self.match(a2lParser.IDENT)

            elif token in [a2lParser.STRING]:
                localctx = a2lParser.ValueStringContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 29
                self.match(a2lParser.STRING)

            elif token in [a2lParser.INT]:
                localctx = a2lParser.ValueIntContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 30
                self.match(a2lParser.INT)

            elif token in [a2lParser.HEX]:
                localctx = a2lParser.ValueHexContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 31
                self.match(a2lParser.HEX)

            elif token in [a2lParser.FLOAT]:
                localctx = a2lParser.ValueFloatContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 32
                self.match(a2lParser.FLOAT)

            elif token in [a2lParser.BEGIN]:
                localctx = a2lParser.ValueBlockContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 33
                self.block()

            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





