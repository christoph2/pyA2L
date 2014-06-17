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
  language = Python;
  //language = Java;
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

@parser::header {
import pya2l.amllib as amllib
}

@parser::members {

}

@lexer::init {
   pass
}


file returns [value]:	
	'/begin' 'A2ML'
	declarations += declaration*
	'/end' 'A2ML'
	{ $value = amllib.File(declarations) }
	-> ^(FILE declaration*)
	;

declaration returns [value]
@init {
typeDefinition = None
blockDefinition = None
}
:	
	(type_definition { typeDefinition = $type_definition.value } | block_definition { blockDefinition = $block_definition.value } ) ';' 
	{ $value = amllib.Declaration(typeDefinition, blockDefinition) }
	-> ^(DECLARATION type_definition? block_definition?)
	;

type_definition returns [value]:	
	typeName = type_name
	{ $value = amllib.TypeDefinition(typeName)}
	-> ^(TYPE_DEFINITION type_name)
	;
	
type_name returns [value]:	
	tagName = TAG? (
	  name = predefined_type_name
	| name = struct_type_name
	| name = taggedstruct_type_name
	| name = taggedunion_type_name
	| name = enum_type_name
	) 
	{ $value = amllib.TypeName(tagName, name) }
	-> ^(PREDEFINED_TYPE $name)
	;
	
predefined_type_name returns [value]:	
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
	{ $value = amllib.PredefinedTypeName(name) }
	-> ^(PREDEFINED_TYPE_NAME $name)
	;
	
block_definition returns [value]:	
	'block' tagName = TAG typeName = type_name  { $value = amllib.BlockDefinition(tagName, typeName)} -> ^(BLOCK TAG type_name)
	;	
	
enum_type_name returns [value]:	
	  (('enum' idValue = ID? '{' enumList = enumerator_list '}' { $value = amllib.EnumType(idValue, enumList) } -> ^(ENUM  ID? enumerator_list))
	| ('enum' idValue = ID { $value = amllib.EnumRefType(idValue) } -> ^(ENUM_REF ID)))
	;	
	
enumerator_list returns [value]
@init {
myList = list()
}
@after {
$value = myList
}
:
	en += enumerator { myList.append(en.value) } (',' en +=enumerator { myList.append(en.value) })*  
//	{ $value = amllib.EnumeratorList(en) }
	-> ^(ENUMERATOR_LIST $en*)	
	;	
	
enumerator returns [value]	:	
	 enumTag = TAG /*KEYWORD*/ ('=' konst = constant)?  
	 { $value = amllib.Enumerator(enumTag, konst) }
	 -> ^(ENUMERATOR TAG constant?)
	;	

struct_type_name returns [value]:	
	   (('struct' idVal = ID? '{' members += struct_member* '}' {$value =amllib.StructType(idVal, members.value) } -> ^(STRUCT  ID? struct_member*)  )
	 | ('struct'  idVal = ID    {$value = amllib.StructRefType(idVal) } -> ^(STRUCT_REF ID))  )
	 ;
	 	
struct_member returns [value]:	
	mem = member ';'
	{ $value = amllib.StructMember(mem.value)  }
	-> ^(STRUCT_MEMBER member)
	;	

member returns [value]:	
	 tname = type_name  specifiers+=array_specifier* 
	 {$value = amllib.Member(tname, specifiers) }
	 -> ^(MEMBER type_name array_specifier*)
	 ;	
	 
array_specifier returns [value]:	
	'[' konstant = constant ']'  
	{ $value = amllib.ArraySpecifier(konstant.value) }
	-> ^(ARRAY_SPECIFIER constant)
	;	
	
taggedstruct_type_name returns[value]:	
	  idVal = ID? 'taggedstruct' ( '{'  members = taggedstruct_member* '}'
	| members = taggedstruct_member*)
	{ $value = amllib.TaggedStructType(idVal, members) }
	-> ^(TAGGED_STRUCT  ID? taggedstruct_member*)
	;
		
taggedstruct_member returns [value]
@init {
multiple = False
structDef = None
blockDef = None
}
:	
	  (taggedstruct_definition ';'  { multiple = False;  structDef = $taggedstruct_definition.value } ->^(TAGGED_STRUCT_MEMBER taggedstruct_definition? )) 
	| ('(' taggedstruct_definition ')' '*' ';'  { multiple = True;  structDef = $taggedstruct_definition.value  } ->^(TAGGED_STRUCT_MEMBER_VAR taggedstruct_definition? ))
	| (block_definition ';' { multiple =  False; blockDef = $block_definition.value } ->^(TAGGED_STRUCT_MEMBER block_definition?))
	| ('(' block_definition ')' '*' ';' { multiple = True; blockDef = $block_definition.value } ->^(TAGGED_STRUCT_MEMBER_VAR  block_definition?))
	{ $value = amllib.TaggedStructMember(structDef, blockDef, multiple) }
	;	

taggedstruct_definition returns [value]
@init {
multiple = False
}
:	
	  tagName = TAG?  mem= member?  { multiple = False }
	| tagName = TAG '(' mem = member ')' '*' ';' { multiple = True }
	{ $value = amllib.TaggedStructDefinition(tagName, mem, multiple)}
	-> ^(TAGGEDSTRUCT_DEFINITION TAG? member?)
	;

taggedunion_type_name	 returns [value]:	
	  (('taggedunion'  idVal = ID? '{' members = tagged_union_member* '}' 
	  { $value = amllib.TaggedUnionType(idVal, members) }
	  -> ^(TAGGED_UNION ID ? tagged_union_member*) )
	| ('taggedunion' idVal = ID { $value = amllib.TaggedUnionRefType(idVal) }-> ^(TAGGED_UNION_REF ID)))
	;
	
tagged_union_member returns [value]:	
	(
	  TAG  mem = member?  ';' 
	| bd = block_definition ';'
	)
	{ $value = amllib.TaggedUnionMember($TAG.text, mem, bd) }
	-> ^(TAGGED_UNION_MEMBER member? block_definition?)
	;	

constant returns [value]:
	  INT  {$value = int($INT.text)}
	| HEX  {$value = int($HEX.text, 16)}
	| FLOAT  {$value = float($FLOAT.text)}
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

