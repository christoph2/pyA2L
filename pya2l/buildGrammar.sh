#!/bin/sh
java org.antlr.v4.Tool -Dlanguage=Python2 -visitor -Xlog -long-messages aml.g4 # -Xlog -Ddebug=true -long-messages
