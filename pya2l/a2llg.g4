/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2020 by Christoph Schueler <cpu12.gems@googlemail.com>

   All Rights Reserved

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License along
  with this program; if not, write to the Free Software Foundation, Inc.,
  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
*/

/*
** A2L Lexer Grammar, used by AML meta-parser.
*/

lexer grammar a2llg;

IDENT: [a-zA-Z_][a-zA-Z_0-9.]*;

fragment
EXPONENT : ('e'|'E') ('+'|'-')? ('0'..'9')+ ;

FLOAT:
   ('+' | '-')?
    (
        ('0'..'9')+ '.' ('0'..'9')* EXPONENT?
    |   '.' ('0'..'9')+ EXPONENT?
    |   ('0'..'9')+ EXPONENT
    | 'NaN'
    | 'INF'
    )
    ;

INT:
      ('+' | '-')? '0'..'9'+
    | '0'('x' | 'X') ('a' .. 'f' | 'A' .. 'F' | '0' .. '9')+
    ;

COMMENT:
    ('//' ~('\n'|'\r')* '\r'? '\n'
    |   '/*' .*? '*/')
        //-> channel(HIDDEN)
        -> channel(1)
    ;

WS  :   (' ' | '\t' | '\r' | '\n') -> skip
    ;

STRING:
    '"' ( ESC_SEQ | ~('\\'|'"') )* '"'
    ;


fragment
HEX_DIGIT : ('0'..'9'|'a'..'f'|'A'..'F') ;

fragment
ESC_SEQ
    :   '\\'
        (   // The standard escaped character set such as tab, newline, etc.
            [btnfr"'\\]
        |   // A Java style Unicode escape sequence
            UNICODE_ESC
        |   // Invalid escape
            .
        |   // Invalid escape at end of file
            EOF
        )
    ;

fragment
UNICODE_ESC
    :   'u' (HEX_DIGIT (HEX_DIGIT (HEX_DIGIT HEX_DIGIT?)?)?)?
;

fragment
OCTAL_ESC:
    '\\' ('0'..'3') ('0'..'7') ('0'..'7')
    |   '\\' ('0'..'7') ('0'..'7')
    |   '\\' ('0'..'7')
    ;


BEGIN:
    '/begin'
    ;

END:
    '/end'
    ;
