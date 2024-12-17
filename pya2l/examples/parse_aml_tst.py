import sys
import os

import enum
import typing

from dataclasses import dataclass, field
from pya2l import amlparser_ext as e


os.chdir(r"C:\csProjects\pyA2L\pya2l\examples")
sys.argv.append(r".\XCP_101.aml")


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
class TaggedUnion:
    name: str
    members: list[typing.Any] = field(default_factory=[])
    
@dataclass
class TaggedUnionMember:
    name: str
    member: typing.Any

@dataclass
class TaggedStruct:
    name: str
    members: list[typing.Any] = field(default_factory=[])
    
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
class Struct:
    name: str
    members: list[typing.Any] = field(default_factory=[])


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
        print_node(root)
        self.do_members(root.content)
        
    def do_members(self, node):        
        print_node(node.get("MEMBERS"))
        for member in node.get("MEMBERS").list:
            tp = member.aml_type
            if tp == e.AmlType.BLOCK:
                self.do_block(member)
            else:
                self.do_type_name(member)
                
    def do_block(self, node):
        tag = node.content.get('TAG').content        
        tp = self.do_type_name(node.content.get('TYPE'))
        print("blk", Block(tag, tp))        
        return Block(tag, tp)
        
    def do_type_name(self, node):
        tp = node.aml_type
        print("TP", tp)
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
        print(result)
        return result
        
    def do_enumeration(self, node):
        name = node.map.get("NAME").content
        values = node.map.get("VALUES")
        print("\tENUM", name, values.content)
        
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
        return TaggedUnion(name, self.do_tagged_union_members(members))
        
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
            else:
                print("")
            result.append(TaggedUnionMember(tag, mem))
        return result
            
    def do_tagged_struct(self, node):
        name = node.map.get("NAME").content
        members = node.map.get("MEMBERS")            
        return TaggedStruct(name, self.do_tagged_struct_members(members))

    def do_tagged_struct_members(self, node):        
        result = []
        for member in node.content:          
            tag = member.map.get("TAG").content
            mem = member.map.get("MEMBER")
            ## print("\tTSM", tag, mem.content)
            result.append(TaggedStructMember(tag, self.do_tagged_struct_definition(mem)))
        return result
            
    def do_tagged_struct_definition(self, node):
        content = node.content
        definition = content.get("DEFINITION")
        multiple = True if content.get("MULTIPLE").content == 1 else False
        ## print("\tTSD", definition.aml_type, definition.content)       
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
        print("MEMBER:", content)
        ## 'ARR_SPEC'
        arr_spec = content.get("ARR_SPEC").content
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

#root = e.unmarshal(res)
#print_node(root)
#print(mem, mem.node_type, mem.aml_type, [c.content for c in mem.content])

