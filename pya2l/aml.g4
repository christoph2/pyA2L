/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2024 by Christoph Schueler <cpu12.gems@googlemail.com>

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
        (d += declaration)*
   '/end' 'A2ML'
   ;

declaration:
   ( t = type_definition ';')
   | (b = block_definition ';')
   ;

type_definition:
   type_name
   ;

type_name:
     pr = predefined_type_name
   | st = struct_type_name
   | ts = taggedstruct_type_name
   | tu = taggedunion_type_name
   | en = enum_type_name
   ;

predefined_type_name:
   (
     name = 'char'
   | name = 'int'
   | name = 'long'
   | name = 'uchar'
   | name = 'uint'
   | name = 'ulong'
   | name = 'int64'
   | name = 'uint64'
   | name = 'double'
   | name = 'float'
   )
   ;

block_definition:
   'block' tag = tagValue (/* blk = block_definition | */ tn = type_name)
   ;

enum_type_name:
      ('enum' t0 = identifierValue? '{' l = enumerator_list '}' )
    | ('enum' t1 = identifierValue)
    ;

enumerator_list:
   ids += enumerator (',' ids += enumerator )*
   ;

enumerator:
   t = tagValue ('=' c = numericValue)?
   ;

struct_type_name:
      'struct' t0 = identifierValue? '{' l += struct_member* '}' ';'?
    | 'struct' t1 = identifierValue
    ;

struct_member:
     m = member ';'?
   ;

member:
    t = type_name (a += array_specifier)*
	| b = block_definition
    ;

array_specifier:
   '[' c = numericValue ']'
   ;

taggedstruct_type_name:
     'taggedstruct' t0 = identifierValue? '{' (l += taggedstruct_member)* '}' ';'?
   | 'taggedstruct' t1 = identifierValue
   ;

taggedstruct_member:
	  ts1 = taggedstruct_definition ';'?
    | '(' ts0 = taggedstruct_definition ';'? ')' '*' ';'
    | bl1 = block_definition ';'?
	| '(' bl0 = block_definition ';'? ')' '*' ';'
    ;

taggedstruct_definition:
      tag = tagValue mem = member?
	| tag = tagValue '(' mem = member ';'? ')' '*'
    ;

taggedunion_type_name:
      'taggedunion' t0 = identifierValue? '{' l += tagged_union_member* '}'
    | 'taggedunion' t1 = identifierValue
    ;

tagged_union_member:
     t = tagValue  m = member? ';'?
   | b = block_definition ';'?
   ;

numericValue:
     i = INT
   | h = HEX
   | f = FLOAT
   ;

stringValue:
    s = STRING
    ;

tagValue:
    s = TAG
    ;

identifierValue:
    i = ID
    ;

/*
** Lexer
*/
INT : '0'..'9'+
    ;

HEX:   '0'('x' | 'X') ('a' .. 'f' | 'A' .. 'F' | '0' .. '9')+
    ;

FLOAT:
    ('+' | '-')?
    (
        ('0'..'9')+ '.' ('0'..'9')* EXPONENT?
    |   '.' ('0'..'9')+ EXPONENT?
    |   ('0'..'9')+ EXPONENT
    )
    ;

ID  : /* ('a'..'z'|'A'..'Z'|'_') */
    ('a'..'z'|'A'..'Z'|'0'..'9'|'_')+
    ;

TAG:  '"' ID '"'  // s. 3.2
   ;

COMMENT
    :   ('//' ~('\n'|'\r')* '\r'? '\n'
    |   '/*' .*? '*/')
        -> channel(HIDDEN)
    ;

WS  :   (' ' | '\t' | '\r' | '\n') -> skip
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
    :   '\\' ('b'|'t'|'n'|'f'|'r'|'\u0022'|'\''|'\\')
    |   OCTAL_ESC
    ;

fragment
OCTAL_ESC
    :   '\\' ('0'..'3') ('0'..'7') ('0'..'7')
    |   '\\' ('0'..'7') ('0'..'7')
    |   '\\' ('0'..'7')
    ;
