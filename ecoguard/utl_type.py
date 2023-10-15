from enum import Enum

class UtlType(Enum):
    ELECTRICITY = ('ELEC', 'con')
    HEATING = ('HEAT', 'con')
    HOT_WATER = ('HW', 'con')
    COLD_WATER = ('CW', 'con')
    TEMPERATURE = ('T', 'val')

    def __init__(self, code, function):
        self.code = code
        self.function = function
    
    @property
    def full_string(self):
        return f"{self.code}[{self.function}]"
