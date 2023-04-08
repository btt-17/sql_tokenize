
class TokenType(object):
    _parent = None
    def __init__(self, name=""):
        self._name = name

    def __getattr__(self, name):
        if self._name == "":     
            child = TokenType(name)
        else:
            child = TokenType(self._name+"."+name)
        setattr(self,name,child)
        child._parent = self
        return child
    
    def __repr__(self) :
        return self._name
    
class Token(object):
    def __init__(self, value, ttype):
        self.value = value
        self.type = ttype

    def __str__(self):
        return self.value
    
    def __add__(self, string):
        return Token(self.value+string,self.type)
    



