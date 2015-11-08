/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2015 by Christoph Schueler <cpu12.gems@googlemail.com>

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

options {
//   debug = 1;
  language = Python;
  //language = Java;
   //output = AST;
   //ASTLabelType = CommonTree;
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


amlFile returns [value]
@init {
declarations = []
}:
   '/begin' 'A2ML'
   (declaration {declarations.append($declaration.value)})*
   '/end' 'A2ML'
   {$value = amllib.File(declarations) }
   //-> ^(FILE declaration*)
   ;

declaration returns [value]
@init {
typeDefinition = None
blockDefinition = None
}
:
   (type_definition {typeDefinition = $type_definition.value } | block_definition {blockDefinition = $block_definition.value } ) ';'
   {$value = amllib.Declaration(typeDefinition, blockDefinition) }
   //-> ^(DECLARATION type_definition? block_definition?)
   ;

type_definition returns [value]:
   typeName = type_name
   {$value = amllib.TypeDefinition($typeName.value)}
   //-> ^(TYPE_DEFINITION type_name)
   ;

type_name returns [value]:
   tagName = TAG? (
     name = predefined_type_name
   | name = struct_type_name
   | name = taggedstruct_type_name
   | name = taggedunion_type_name
   | name = enum_type_name
   )
   {$value = amllib.TypeName($name.value, $name.text) }
   //-> ^(PREDEFINED_TYPE $name)
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
   {$value = amllib.PredefinedTypeName($name.text) }
   //-> ^(PREDEFINED_TYPE_NAME $name)
   ;

block_definition returns [value]:
   'block' tagName = TAG typeName = type_name  
   {$value = amllib.BlockDefinition($tagName, $typeName.value)} 
   //-> ^(BLOCK TAG type_name)
   ;

enum_type_name returns [value]:
     (('enum' idVal0 = ID? '{' enumList = enumerator_list '}' {$value = amllib.EnumType($idVal0, $enumList.value) } )
     //-> ^(ENUM  identifier? enumerator_list))
      | ('enum' idVal1 = ID {$value = amllib.EnumRefType($idVal1) } 
     //-> ^(ENUM_REF identifier)
     ))
   ;

enumerator_list returns [value]
@init {
myList = list()
}
@after {
$value = [e.value for e in $en] # myList
}
:
   en += enumerator {myList.append($en) } (',' en +=enumerator {myList.append($en) })*
// { $value = amllib.EnumeratorList(en) }
   //-> ^(ENUMERATOR_LIST $en*)
   ;

enumerator returns [value]
@init {
result = None
}
:
    enumTag = TAG /*KEYWORD*/ ('=' konst = constant)?
    {result = amllib.Enumerator($enumTag, $konst.value); $value = (result.tag, result.value); }
    //-> ^(ENUMERATOR TAG constant?)
   ;

struct_type_name returns [value]
@init {
members = []
}:
      (('struct' idVal = ID? '{' (struct_member {members.append($struct_member.value)}) * '}' {$value =amllib.StructType($idVal, members) } )
    //-> ^(STRUCT  ID? struct_member*)  )
    | ('struct'  idVal = ID    {$value = amllib.StructRefType($idVal) } ))
    //-> ^(STRUCT_REF ID))  )
    ;

struct_member returns [value]:
   mem = member ';'
   {$value = amllib.StructMember($mem.value) }
   //-> ^(STRUCT_MEMBER member)
   ;

member returns [value]
@init {
specifiers = []
}:
    tname = type_name  (array_specifier {specifiers.append($array_specifier.value) })*
    {$value = amllib.Member($tname.value, specifiers) }
    //-> ^(MEMBER type_name array_specifier*)
    ;

array_specifier returns [value]:
   '[' konstant = constant ']'
   {$value = amllib.ArraySpecifier($konstant.value) }
   //-> ^(ARRAY_SPECIFIER constant)
   ;

taggedstruct_type_name returns[value]:
     {$idVal = None} idVal = ID? {$value = amllib.TaggedStructType($idVal) } 'taggedstruct' ( '{'  (member0 = taggedstruct_member {$value.append($member0.value) })*   '}'
   | (member1 = taggedstruct_member {$value.append(member1.value) })*)
   //-> ^(TAGGED_STRUCT  ID? taggedstruct_member*)
   ;

taggedstruct_member returns [value]
@init {
multiple = False
structDef = None
blockDef = None
}
:
     (taggedstruct_definition ';'  {multiple = False;  structDef = $taggedstruct_definition.value } )
    //->^(TAGGED_STRUCT_MEMBER taggedstruct_definition? ))
   | ('(' taggedstruct_definition ')' '*' ';'  {multiple = True;  structDef = $taggedstruct_definition.value  } )
    //->^(TAGGED_STRUCT_MEMBER_VAR taggedstruct_definition? ))
   | (block_definition ';' {multiple =  False; blockDef = $block_definition.value } )
    //->^(TAGGED_STRUCT_MEMBER block_definition?))
   | ('(' block_definition ')' '*' ';' {multiple = True; blockDef = $block_definition.value } )
    //->^(TAGGED_STRUCT_MEMBER_VAR  block_definition?))
   {$value = amllib.TaggedStructMember(structDef, blockDef, multiple) }
   ;

taggedstruct_definition returns [value]
@init {
multiple = False
}
:
     tagName = TAG?  mem= member?  {multiple = False }
   | tagName = TAG '(' mem = member ')' '*' ';' {multiple = True }
   {$value = amllib.TaggedStructDefinition(tagName, mem, multiple)}
   //-> ^(TAGGEDSTRUCT_DEFINITION TAG? member?)
   ;

taggedunion_type_name    returns [value]:
     (('taggedunion'  idVal = ID? '{' members = tagged_union_member* '}'
     {$value = amllib.TaggedUnionType($idVal, $members.value) })
     //-> ^(TAGGED_UNION ID ? tagged_union_member*) )
   | ('taggedunion' idVal = ID {$value = amllib.TaggedUnionRefType($idVal) }))
    //-> ^(TAGGED_UNION_REF ID)))
   ;

tagged_union_member returns [value]:
   (
     TAG  mem = member?  ';'
   | bd = block_definition ';'
   )
   {member = None if not localctx.mem else $mem.value; block = None if not localctx.bd else $bd.value; $value = amllib.TaggedUnionMember($TAG.text, member, block) }
   //-> ^(TAGGED_UNION_MEMBER member? block_definition?)
   ;

constant returns [value]:
     INT  {$value = int($INT.text)}
   | HEX  {$value = int($HEX.text, 16)}
   | FLOAT  {$value = float($FLOAT.text)}
   ;
   
/*
identifier returns [value]:	
	ID
	{$value = $ID.text }
	;   
*/

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
    // ANTLR3
    //:   '//' ~('\n'|'\r')* '\r'? '\n' { $channel = HIDDEN; }
    //|   '/*' ( options {greedy=false;} : . )* '*/' { $channel = HIDDEN; }

    // ANTLR4
    :   ('//' ~('\n'|'\r')* '\r'? '\n'
    |   '/*' .*? '*/')
        -> channel(HIDDEN)
    ;

WS  :   ( ' '
        | '\t'
        | '\r'
        | '\n'
        )   //{$channel=HIDDEN;}
        -> channel(HIDDEN)
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

