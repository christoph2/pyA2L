/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2014 by Christoph Schueler <github.com/Christoph2,
                                        cpu12.gems@googlemail.com>

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

grammar aml;

options {
//   debug = 1;
  //language = Python;
  language = Java;
   output = AST;
   ASTLabelType = CommonTree;
   //k = 2;
   //debug = true;
   //backtrack = true;
   //memoize = true;   
}

tokens {
	FILE;
	BLOCK;
	DECLARATION;
	ENUM;
	ENUM_REF;
	ENUMERATOR;
	ENUMERATOR_LIST;
	STRUCT;
	STRUCT_REF;
	STRUCT_MEMBER;
	TAGGED_UNION;
	TAGGED_UNION_MEMBER;
	TAGGED_UNION_REF;
	TAGGED_STRUCT;
	TAGGED_STRUCT_REF;
	TAGGED_STRUCT_MEMBER;
	TAGGED_STRUCT_MEMBER_VAR;	
	TAGGEDSTRUCT_DEFINITION;
	MEMBER;
	TYPE_DEFINITION;
	ARRAY_SPECIFIER;
	PREDEFINED_TYPE;
	PREDEFINED_TYPE_NAME;
}

file:	'/begin' 'A2ML'
	declaration*
	'/end' 'A2ML'
	-> ^(FILE declaration*)
	;

declaration:	
	(type_definition | block_definition) ';' -> ^(DECLARATION type_definition? block_definition?)
	;

type_definition:	
	type_name
	-> ^(TYPE_DEFINITION type_name)
	;
	
type_name:	
	TAG? (
	  name = predefined_type_name
	| name = struct_type_name
	| name = taggedstruct_type_name
	| name = taggedunion_type_name
	| name = enum_type_name
	) -> ^(PREDEFINED_TYPE $name)
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
	) -> ^(PREDEFINED_TYPE_NAME $name)
	;
	
block_definition:	
	'block' TAG type_name -> ^(BLOCK TAG type_name)
	;	
	
enum_type_name:	
	  (('enum' ID? '{' enumerator_list '}' -> ^(ENUM  ID? enumerator_list))
	| ('enum' ID -> ^(ENUM_REF ID)))
	;	
	
enumerator_list:	
	en += enumerator (',' en +=enumerator)*  -> ^(ENUMERATOR_LIST $en*)
	;	
	
enumerator	:	
	 TAG /*KEYWORD*/ ('=' constant)?  -> ^(ENUMERATOR TAG constant?)
	;	

struct_type_name:	
	   (('struct' ID? '{'struct_member* '}' -> ^(STRUCT  ID? struct_member*))
	 | ('struct'  ID	 -> ^(STRUCT_REF ID)) )
	 ;
	 	
struct_member:	
	member ';'
	-> ^(STRUCT_MEMBER member)
	;	

member:	
	 type_name  array_specifier* -> ^(MEMBER type_name array_specifier*)
	 ;	
	 
array_specifier:	
	'[' constant ']'  -> ^(ARRAY_SPECIFIER constant)
	;	
	
taggedstruct_type_name:	
	  ID? 'taggedstruct' ( '{'  taggedstruct_member* '}'
	| taggedstruct_member*)
	-> ^(TAGGED_STRUCT  ID? taggedstruct_member*)
	;
		
taggedstruct_member:	
	  (taggedstruct_definition ';'  ->^(TAGGED_STRUCT_MEMBER taggedstruct_definition? )) 
	| ('(' taggedstruct_definition ')' '*' ';'  ->^(TAGGED_STRUCT_MEMBER_VAR taggedstruct_definition? ))
	| (block_definition ';' ->^(TAGGED_STRUCT_MEMBER block_definition?))
	| ('(' block_definition ')' '*' ';' ->^(TAGGED_STRUCT_MEMBER_VAR  block_definition?))
	;	

taggedstruct_definition:	
	  TAG?  member? 
	|  TAG '(' member ')' '*' ';'
	-> ^(TAGGEDSTRUCT_DEFINITION TAG? member?)
	;

taggedunion_type_name	:	
	  (('taggedunion'  ID? '{' tagged_union_member* '}' -> ^(TAGGED_UNION ID ? tagged_union_member*) )
	| ('taggedunion' ID -> ^(TAGGED_UNION_REF ID)))
	;
	
tagged_union_member:	
	(
	  TAG  member?  ';' 
	| block_definition ';'
	)
	-> ^(TAGGED_UNION_MEMBER member? block_definition?)
	;	

constant:
	  INT 
	| HEX
	| FLOAT
	;
/*
** Lexer
*/
ID  :	('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')*
    ;
    
TAG:	'"' ID '"'	// s. 3.2
   ;    
   
//KEYWORD:	'"' ID '"'
//   ;       

INT :	'0'..'9'+
    ;
    
HEX:	 '0'('x' | 'X') ('a' .. 'f' | 'A' .. 'F' | '0' .. '9')+
    ;
	    

FLOAT
    :   ('0'..'9')+ '.' ('0'..'9')* EXPONENT?
    |   '.' ('0'..'9')+ EXPONENT?
    |   ('0'..'9')+ EXPONENT
    ;

COMMENT
    :   '//' ~('\n'|'\r')* '\r'? '\n' {$channel=HIDDEN;}
    |   '/*' ( options {greedy=false;} : . )* '*/' {$channel=HIDDEN;}
    ;

WS  :   ( ' '
        | '\t'
        | '\r'
        | '\n'
        ) {$channel=HIDDEN;}
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

/*

*/