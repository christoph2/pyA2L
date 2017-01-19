/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2016 by Christoph Schueler <cpu12.gems@googlemail.com>

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

grammar aml;

amlFile:
   '/begin' 'A2ML'
        (declaration)*
   '/end' 'A2ML'
   ;

declaration:
   (type_definition
    | block_definition) ';'
   ;

type_definition:
   type_name
   ;

type_name:
   TAG? (
     name = predefined_type_name
   | name = struct_type_name
   | name = taggedstruct_type_name
   | name = taggedunion_type_name
   | name = enum_type_name
   )
   ;

predefined_type_name:
   (
     name = 'char'
   | name = 'int'
   | name = 'long'
   | name = 'uchar'
   | name = 'uint'
   | name = 'ulong'
   | name = 'double'
   | name = 'float'
   )
   ;

block_definition:
   'block' TAG type_name
   ;

enum_type_name:
      ('enum' ID? '{' enumerator_list '}' )
    | ('enum' ID)
    ;

enumerator_list:
   { print(_input.LA(1)) } enumerator (',' enumerator )*
   ;

enumerator:
    TAG ('=' constant)?
   ;

struct_type_name:
    (('struct' ID? '{' struct_member * '}')
    | ('struct' ID))
    ;

struct_member:
   member ';'
   ;

member:
    type_name (array_specifier)*
    ;

array_specifier:
   '[' constant ']'
   ;

taggedstruct_type_name:
    ID? 'taggedstruct' ('{' (taggedstruct_member)* '}' | ID)
   | (taggedstruct_member)*)
   ;

taggedstruct_member:
    (taggedstruct_definition ';')
    | ('(' taggedstruct_definition ')' '*' ';')
    | (block_definition ';')
    | ('(' block_definition ')' '*' ';')
   ;

taggedstruct_definition:
   TAG member
   | TAG '(' member ')' '*' ';'
   ;

taggedunion_type_name:
    (('taggedunion' ID? '{' tagged_union_member* '}')
    | ('taggedunion' ID))
    ;

tagged_union_member:
   (
     TAG  member?  ';'
   | block_definition ';'
   )
   ;

constant returns [value]:
     INT  {$value = int($INT.text)}
   | HEX  {$value = int($HEX.text, 16)}
   | FLOAT  {$value = float($FLOAT.text)}
   ;


/*
** Lexer
*/
ID  : ('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')*
    ;

TAG:  '"' ID '"'  // s. 3.2
   ;

//KEYWORD:  '"' ID '"'
//   ;

INT : '0'..'9'+
    ;

HEX:   '0'('x' | 'X') ('a' .. 'f' | 'A' .. 'F' | '0' .. '9')+
    ;

FLOAT
    :   ('0'..'9')+ '.' ('0'..'9')* EXPONENT?
    |   '.' ('0'..'9')+ EXPONENT?
    |   ('0'..'9')+ EXPONENT
    ;

COMMENT
    :   ('//' ~('\n'|'\r')* '\r'? '\n'
    |   '/*' .*? '*/')
        -> channel(HIDDEN)
    ;

WS  :   (' ' | '\t' | '\r' | '\n') -> channel(HIDDEN)
    ;

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

