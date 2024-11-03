

LISTBOX_MIMETYPE = "application/x-item"
OP_NODE_INPUT= 1
OP_NODE_OUTPUT = 2
OP_NODE_ADD = 3
OP_NODE_SUBSTRACT = 4
OP_NODE_MULTIPLY = 5
OP_NODE_DIVIDE = 6


CALC_NODES = {

}

class ConfException(Exception): pass
class InvalidNodeRegistration(ConfException): pass
class OPCodeNotRegistered(ConfException): pass

def registerNodeNow(opCode, classReference):
    if opCode in CALC_NODES:
        raise InvalidNodeRegistration("Dubplicate Node Registration of '%s'. There is already %s"
                                          % (opCode, CALC_NODES[opCode]
                                      ))
    CALC_NODES[opCode] = classReference

def registerNode(opCode):
    def decorator(originalClass):
        registerNodeNow(opCode, originalClass)
        return originalClass
    return decorator

def getClassFromOPCode(opCode):
    if opCode not in CALC_NODES: raise OPCodeNotRegistered("OPCode '%d' is not registered" % opCode)
    return CALC_NODES[opCode]