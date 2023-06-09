"""Python class for storing save information as an object"""
from typing import List, Union

from util.locations import locations


def hexExtendor(val, length = 8):
    """

    :param val:
    :return:
    """
    return hex(val)[2:].zfill(length)


def convertFromHex(val: str, valtype: type) -> Union[int, str, list, TypeError]:
    """
    Convert a vlue from reverse hex to str/int
    :param val: Reverse Hex value
    :param valtype: What to convert to
    :return: Int or Str conversion of Reverse hex
    """
    if valtype == int:
        hexval = ""
        for i in range(len(val) - 2, -1, -2):
            hexval += val[i] + val[i + 1]
        return int(hexval, 16)
    elif valtype == str:
        newval = ""
        for i in range(len(val) - 2, -1, -2):
            newval += chr(int(val[i] + val[i + 1], 16))
        return newval
    elif valtype == list:
        newval = []
        for i in range(3):
            hexval = ""
            for j in range(i*4-1, (i-1)*4-1, -2):
                hexval += val[j] + val[j + 1]
            newval.append(hexval)
        newval = [int(val, 16) for val in newval]
        return newval
    else:
        return TypeError("Invalid conversion target type: "+str(valtype))


def convertToHex(val: Union[int, str, list]) -> Union[str, TypeError]:
    """
    Convert a given int or str to the save file's reverse hex format
    :param val: Value to convert
    :return: Reversed Hex
    """
    if type(val) == int:
        hexval = hexExtendor(val)
        newhexval = ""
        for i in range(len(hexval)-2, -1, -2):
            newhexval += hexval[i]+hexval[i+1]
        return newhexval
    elif type(val) == str:
        try:
            return convertToHex(int(val))
        except ValueError:
            hexval = ""
            for char in val:
                hexval += hexExtendor(ord(char), 2)
            newhexval = ""
            for i in range(len(hexval) - 2, -1, -2):
                newhexval += hexval[i] + hexval[i + 1]
            return newhexval
    elif type(val) == list:
        hexlist = [hexExtendor(listval, 4) for listval in val]


    else:
        return TypeError("Invalid conversion source type: "+str(type(val)))


class Save:
    """
    Class for the save data currently known in the game
    """
    def __init__(self):
        self.timestamp: int
        self.version: str
        self.elapsed: int
        self.deathcounter: int
        self.slot: int
        """
        1. Village Intro
        3. A New Friend
        4. Getting to know each other
        5. The Cave
        6. The Highlands
        7. The Swamp
        9. The Shipwreck
        10. In Control
        12. Archipelago 1
        14. The Desert
        15. The Desert Hut
        16. The Robot Base
        17. Home
        """
        self.__chapters = (1, 3, 4, 5, 6, 7, 9, 10, 12, 14, 15, 16, 17)
        self.chapterId: int
        self.sceneId: int
        self.position: List[int]

        self.__locations = locations

    def get(self, attr: Union[str, int]) -> Union[int, str, AttributeError, KeyError]:
        """
        Get values based on either address or value name
        :param attr: Attribute to get
        :return: Value | Error
        """
        if type(attr) == int:
            for location in self.__locations:
                if location[0] == attr:
                    return convertToHex(self.__getattribute__(location[2]))
            return KeyError("No such save location currently known: "+str(attr))

        else:
            if attr[:2] == "__":
                return AttributeError("Trying to access protected value: "+str(attr))
            attribute = self.__getattribute__(attr)
            if not attribute:
                return KeyError("No such save value currently known: "+str(attr))
            else:
                return convertToHex(attribute)

    def set(self, key: Union[str, int], val: str) -> Union[None, KeyError, AttributeError]:
        """
        store values inside the class
        :param key: Key to store to
        :param val: Value to store
        :return: None | Error
        """
        val = convertFromHex(val, type(key))
        if type(key) == int:
            for location in self.__locations:
                if location[0] == key:
                    self.__setattr__(location[2], val)
                    return
            return KeyError("No such save location currently known: "+str(key))
        else:
            if key[:2] == "__":
                return AttributeError("Trying to access protected value: "+str(key))
            for location in self.__locations:
                if location[2] == key:
                    self.__setattr__(key, val)
                    return
            return KeyError("No such save value currently known: "+str(key))