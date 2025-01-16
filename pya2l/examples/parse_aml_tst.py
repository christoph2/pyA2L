import sys
import os
from pprint import pprint

import enum
import typing

from dataclasses import dataclass, field
from pya2l import amlparser_ext as e


os.chdir(r"C:\csProjects\pyA2L\pya2l\examples")
# sys.argv.append(r".\XCP_101.aml")
sys.argv.append(r".\AML.tmp")


CPLX = """
/begin IF_DATA ASAP1B_CCP
   /begin SOURCE
      \"segment synchronous event channel\"
      103
      1
      /begin QP_BLOB
          0
          LENGTH 8
          CAN_ID_FIXED 0x330
          FIRST_PID 0
          RASTER 0
      /end QP_BLOB
  /end SOURCE

   /begin SOURCE
      \"10ms time synchronous event channel\"
      4
      1
      /begin QP_BLOB
          1
          LENGTH 12
          CAN_ID_FIXED 0x340
          FIRST_PID 8
          RASTER 1
      /end QP_BLOB
  /end SOURCE

   /begin SOURCE
      \"100ms time synchronous event channel\"
      4
      10
      /begin QP_BLOB
          2
          LENGTH 8
          CAN_ID_FIXED 0x350
          FIRST_PID 20
          RASTER 2
      /end QP_BLOB
  /end SOURCE

   /begin RASTER
      \"segment synchronous event channel\"
      \"seg_sync\"
      0
      103
      1
  /end RASTER

   /begin RASTER
      \"10ms time synchronous event channel\"
      \"10_ms\"
      1
      4
      1
  /end RASTER

   /begin RASTER
      \"100ms time synchronous event channel\"
      \"100_ms\"
      2
      4
      10
  /end RASTER

  /begin SEED_KEY
       \"\"
       \"\"
       \"\"
  /end SEED_KEY

  /begin TP_BLOB
       0x200
       0x202
       0x200
       0x210
       0x1234
       1
       
      /begin CAN_PARAM
           0x3E8
           0x40
           0x16
      /end CAN_PARAM
       
      DAQ_MODE    BURST
      CONSISTENCY DAQ
       
      /begin CHECKSUM_PARAM 
           0xC001
           0xFFFFFFFF
          CHECKSUM_CALCULATION ACTIVE_PAGE
       /end CHECKSUM_PARAM 
       
      /begin DEFINED_PAGES
          1
          \"reference page\"
           0x00
           0x8E0670
           0x1C26C
          ROM
      /end DEFINED_PAGES
       
      /begin DEFINED_PAGES
          2
          \"working page\"
           0x00
           0x808E0670
           0x1C26C
          RAM
          RAM_INIT_BY_ECU
      /end DEFINED_PAGES
       
      OPTIONAL_CMD 0x11  
      OPTIONAL_CMD 0xE  
      OPTIONAL_CMD 0x19  
      OPTIONAL_CMD 0x9  
      OPTIONAL_CMD 0xC  
      OPTIONAL_CMD 0xD  
      OPTIONAL_CMD 0x12  
      OPTIONAL_CMD 0x13  
  /end TP_BLOB
/end IF_DATA
"""

tokens = e.ifdata_lexer(CPLX)
for token in tokens:
    print(token)

"""
while True:
    tok = ifd.next_token()
    print(tok)
    ifd.consume()
    if tok is None:
        break    
"""        

def print_node(node):
    print(node.node_type, node.aml_type, node.content)


class ReferrerType(enum.IntEnum):
    Enumeration      = 0
    StructType       = 1
    TaggedStructType = 2
    TaggedUnionType  = 3    

class AMLPredefinedType(enum.IntEnum):
    CHAR   = 0
    INT    = 1
    LONG   = 2
    UCHAR  = 3
    UINT   = 4
    ULONG  = 5
    DOUBLE = 6
    FLOAT  = 7

@dataclass
class Referrer:
    category: str
    identifier: str

@dataclass
class PDT:
    type: int


@dataclass
class Block:
    tag: str
    type_name: typing.Any

@dataclass
class Enum:
    name: str
    values: typing.Dict[str, int]

@dataclass
class TaggedUnionMember:
    tag: str
    member: typing.Any


@dataclass
class TaggedUnion:
    name: str
    members: list[typing.Any] = field(default_factory=[])
    tags: typing.Dict[str, TaggedUnionMember] = field(default_factory=dict)
        
@dataclass
class TaggedStructMember:
    tag: str
    member: typing.Any

@dataclass
class TaggedStructDefinition:
    multiple: bool
    definition: typing.Any
    block: typing.Any

@dataclass
class TaggedStruct:
    name: str
    members: list[TaggedStructMember] = field(default_factory=[])
    tags: typing.Dict[str, TaggedStructDefinition] = field(default_factory=dict)


@dataclass
class Struct:
    name: str
    members: list[typing.Any] = field(default_factory=list)


@dataclass
class StructMember:
    member: typing.Any

@dataclass
class Member:
    arr_spec: list[int]
    type_name: typing.Any
    block: typing.Optional[Block]


class TreeCreator:
    
    def __init__(self, root):
        if not hasattr(root, "map") and "MEMBERS" not in root.map:
            raise TypeError(f"{root} is not a root node.")
        self.tree = self.do_members(root.content)
        
    def do_members(self, node):
        result = []
        for member in node.get("MEMBERS").list:
            tp = member.aml_type
            if tp == e.AmlType.BLOCK:
                result.append(self.do_block(member))
            else:
                result.append(self.do_type_name(member))
        return result
                
    def do_block(self, node):
        tag = node.content.get('TAG').content        
        tp = self.do_type_name(node.content.get('TYPE'))
        return Block(tag, tp)
        
    def do_type_name(self, node):
        tp = node.aml_type
        if tp == e.AmlType.PDT:
            result = PDT(AMLPredefinedType(node.content))
        elif tp == e.AmlType.STRUCT:
            result = self.do_struct(node)
        elif tp == e.AmlType.TAGGED_STRUCT:
            result = self.do_tagged_struct(node)
        elif tp == e.AmlType.TAGGED_UNION:
            result = self.do_tagged_union(node)
        elif tp == e.AmlType.ENUMERATION:
            result = self.do_enumeration(node)
        elif tp == e.AmlType.REFERRER:
            category = ReferrerType(node.content.get("CATEGORY").content)
            identifier = node.content.get("IDENTIFIER").content
            result = Referrer(category, identifier)
        return result
        
    def do_enumeration(self, node):
        name = node.map.get("NAME").content
        values = node.map.get("VALUES")
        values_dict = {}
        for item in values.content:
            cnt = item.content
            name = cnt.get('NAME').content
            value = cnt.get('VALUE').content
            values_dict[name] = value
        return Enum(name, values_dict)
        
    def do_struct(self, node):
        name = node.map.get("NAME").content
        members = node.map.get("MEMBERS")        
        return Struct(name, self.do_struct_members(members))
        
    def do_struct_members(self, node):
        result = []
        for member in node.content:
            result.append(StructMember(self.do_member(member.map.get("MEMBER"))))
        return result
        
    def do_tagged_union(self, node):
        name = node.map.get("NAME").content
        members = node.map.get("MEMBERS")
        result = self.do_tagged_union_members(members)
        return TaggedUnion(name, result, {mem.tag: mem.member for mem in result})
        
    def do_tagged_union_members(self, node):
        result = []
        for item in node.content:            
            member_map = item.map
            member = member_map.get("MEMBER")
            tag = member_map.get("TAG").content
            if member.aml_type == e.AmlType.BLOCK:
                mem = self.do_block(member)
            elif member.aml_type == e.AmlType.MEMBER:
                mem = self.do_member(member)
            result.append(TaggedUnionMember(tag, mem))
        return result
            
    def do_tagged_struct(self, node):
        name = node.map.get("NAME").content
        members = node.map.get("MEMBERS")
        result = self.do_tagged_struct_members(members)
        return TaggedStruct(name, result,  {mem.tag: mem.member for mem in result})

    def do_tagged_struct_members(self, node):        
        result = []
        for member in node.content:          
            tag = member.map.get("TAG").content
            mem = member.map.get("MEMBER")
            result.append(TaggedStructMember(tag, self.do_tagged_struct_definition(mem)))
        return result
            
    def do_tagged_struct_definition(self, node):
        content = node.content
        definition = content.get("DEFINITION")
        multiple = True if content.get("MULTIPLE").content == 1 else False       
        if definition.aml_type == e.AmlType.BLOCK:
            tp = definition.content.get("TYPE")
            return TaggedStructDefinition(multiple, None, self.do_block(definition))
        elif definition.aml_type == e.AmlType.TAGGED_STRUCT_DEFINITION:            
            member = definition.content.get("MEMBER")
            res = self.do_member(member)
            if res is not None:
                return TaggedStructDefinition(multiple, res, None)
            else:
                return TaggedStructDefinition(multiple, None, None)
                
        
    def do_member(self, node):
        if node.aml_type == e.AmlType.NONE:
            return
        if node.aml_type != e.AmlType.MEMBER        :
            return
        content = node.map
        arr_spec = tuple([c.content for c in content.get("ARR_SPEC").content])
        is_block = content.get("IS_BLOCK").content
        block_type = content.get("NODE")
        if is_block:
            blk = self.do_block(block_type)
            tp = None
        else:
            tp = self.do_type_name(block_type)
            blk = None        
        return Member(arr_spec, tp, blk)
            

data = open(sys.argv[1], encoding="latin-1").read()
res = e.parse_aml(data)

tv = TreeCreator(e.unmarshal(res))
print(tv.tree)


