from enum import Enum

class UtlType(Enum):
    ELECTRICITY = 'ELEC[con]'
    HEATING = 'HEAT[con]'
    HOT_WATER = 'HW[con]'
    COLD_WATER = 'CW[con]'
    TEMPERATURE = 'T[val]'