

def dump(tree, level = 0):
    level += 1

    print "%s%s ==> %s" % (("  " * level), tree.getType(), tree.getText())
    for ch in tree.getChildren():
        dump(ch, level)
    level -= 1

