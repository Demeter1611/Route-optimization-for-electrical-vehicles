class Node:
    def __init__(self, id, x, y, demand=0, type='customer'):
        self._id = id
        self._x = x
        self._y = y
        self._demand = demand
        self._type = type
    
    @property
    def id(self):
        return self._id

    @property
    def x(self):
        return self._x
    
    @property
    def y(self):
        return self._y
    
    @property
    def demand(self):
        return self._demand
    
    @property
    def type(self):
        return self._type
 
    @demand.setter
    def demand(self, value):
        self._demand = value
    
    @type.setter
    def type(self, value):
        allowed_types = ['depot', 'customer', 'station']
        if value not in allowed_types:
            raise ValueError("Invalid type")
        self._type = value
    
    def __repr__(self):
        return f"Node(ID: {self.id:4} | Pos: ({self.x:6.1f}, {self.y:6.1f}) | Demand: {self.demand:3} | Type: {self.type:8})"
