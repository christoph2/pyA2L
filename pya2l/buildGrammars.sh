#!/bin/bash
java org.antlr.v4.Tool -Dlanguage=Python2 -long-messages aml.g4 -o ./py2/
java org.antlr.v4.Tool -Dlanguage=Python3 -long-messages aml.g4 -o ./py3/
java org.antlr.v4.Tool -Dlanguage=Python2 -long-messages -visitor a2l.g4 -o ./py2/
java org.antlr.v4.Tool -Dlanguage=Python3 -long-messages -visitor a2l.g4 -o ./py3/
