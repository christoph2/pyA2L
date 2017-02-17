/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2017 by Christoph Schueler <cpu12.gems@googlemail.com>

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

//
//  Requires ANTLR >= 4.5.1 !!!
//

grammar a2l;

/*

//amlFile:
//   BEGIN
//        (declaration)*
//   END
//   ;


/*
json:   obj
    |   array
    ;

obj
    :   '{' pair (',' pair)* '}'    # AnObject
    |   '{' '}'                     # EmptyObject
    ;

array
    :   '[' value (',' value)* ']'  # ArrayOfValues
    |   '[' ']'                     # EmptyArray
    ;

pair:   STRING ':' value ;

value
    :   STRING      # String
    |   NUMBER      # Atom
    |   obj         # ObjectValue
    |   array       # ArrayValue
    |   'true'      # Atom
    |   'false'     # Atom
    |   'null'      # Atom
    ;
*/

a2lFile:
    version?
    block;

version:
    ASAP2_VERSION v0 = INT v1 = INT;

block:
    BEGIN  kw0 = IDENT value* END kw1 = IDENT
    //INCLDUE STRING
    ;

value:
      IDENT     # valueIdent
     | STRING   # valueString
     | INT      # valueInt
     | HEX      # valueHex
     | FLOAT    # valueFloat
     | block    # valueBlock
    ;

ASAP2_VERSION: 'ASAP2_VERSION';

INCLUDE: '/include';

BEGIN: '/begin';

END: '/end';


// constant returns [value]:
//     INT  {$value = int($INT.text)}
//   | HEX  {$value = int($HEX.text, 16)}
//   | FLOAT  {$value = float($FLOAT.text)}
//   ;

INT: ('+' | '-')? '0'..'9'+
    ;

HEX:   '0'('x' | 'X') ('a' .. 'f' | 'A' .. 'F' | '0' .. '9')+
    ;

FLOAT
    :   ('0'..'9')+ '.' ('0'..'9')* EXPONENT?
    |   '.' ('0'..'9')+ EXPONENT?
    |   ('0'..'9')+ EXPONENT
    ;


//          \b"(?P<STRING>[^"]*?)"\b
//       | \b(?P<BEGIN>/begin)\b
//        | \b(?P<END>/end)\b
//        | \b(?P<IDENT>[a-zA-Z_][a-zA-Z_0-9.|]*)\b
//        | \b(?P<NUMBER>
//                  (0(x|X)?[0-9a-fA-F]+)
//                | ((\+ | \-)?\d+)
COMMENT
    :   ('//' ~('\n'|'\r')* '\r'? '\n'
    |   '/*' .*? '*/')
        -> channel(HIDDEN)
    ;

WS  :   (' ' | '\t' | '\r' | '\n') -> channel(HIDDEN)
    ;

IDENT: [a-zA-Z_][a-zA-Z_0-9.]*;

STRING
    :  '"' ( ESC_SEQ | ~('\\'|'"') )* '"'
    ;

fragment
EXPONENT : ('e'|'E') ('+'|'-')? ('0'..'9')+ ;

fragment
HEX_DIGIT : ('0'..'9'|'a'..'f'|'A'..'F') ;

fragment
ESC_SEQ
    :   '\\' ('b'|'t'|'n'|'f'|'r'|'\"'|'\''|'\\')
    |   OCTAL_ESC
    ;

fragment
OCTAL_ESC
    :   '\\' ('0'..'3') ('0'..'7') ('0'..'7')
    |   '\\' ('0'..'7') ('0'..'7')
    |   '\\' ('0'..'7')
    ;

