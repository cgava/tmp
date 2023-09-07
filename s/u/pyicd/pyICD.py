"""
ICD as a python object
See ate2009.ecore file
"""
import logging

logger = logging.getLogger("ate2009-ICD-parser")

class ICD(object):
    def __init__(self, loglevel=logging.WARNING):
        self.dict_index = {}
        self.devices = []
        self.bus = None
        self.name = ""
        logger.setLevel(loglevel)

class Bus(object):
    def __init__(self, **kwargs):
        self.channels = []
        self.datas = []
        self.filters = []

class IndexedElement(object):
    def __init__(self, dict_index, **kwargs):
        self._index = int(kwargs.get("index", None))
        if self._index is None:
            raise ValueError('Indexed element has non index')
        logger.debug(f'Adding index {self._index} for Element')
        dict_index[self._index] = self

class ICDElement(IndexedElement):
    """Parent class for Device, Channel, Container, Data and Filter"""
    def __init__(self, dict_index, **kwargs):
        super(ICDElement, self).__init__(dict_index, **kwargs)
        self._comment = kwargs.get("comment", None)
        self._name = kwargs.get("name", None)
        self.parents = []
        self.configs = []
        

    def get_comment(self):
        return self._comment

    def get_name(self):
        return self._name

    def get_index(self):
        return self._index

class Config(object):
    def __init__(self, **kwargs):
        self._property = kwargs.get("property", "")
        self._value = kwargs.get("value", "")
        self._type = kwargs.get("type", "")
        self._comment = kwargs.get("comment", "")
        self._value_pattern = kwargs.get("valuePattern", "")
        self._hidden = kwargs.get("hidden", False)
        self._displayed = kwargs.get("displayed", False)
        self._value_format = kwargs.get("valueFormat", "")
        self._type_changed = kwargs.get("typeChanged", False)
        self._symbols = kwargs.get("symbols", "")

    def get_property(self):
        return self._property

    def get_value(self):
        return self._value

    def get_type(self):
        return self._type

    def get_comment(self):
        return self._comment

    def get_value_pattern(self):
        return self._value_pattern

    def get_hidden(self):
        return self._hidden

    def get_displayed(self):
        return self._displayed

    def get_value_format(self):
        return self._value_format

    def get_type_changed(self):
        return self._type_changed

    def get_symbols(self):
        return self._symbols


class Device(ICDElement):
    """Generic class for devices"""

    def __init__(self, dict_index, **kwargs):
        ICDElement.__init__(self, dict_index, **kwargs)
        self.channels = kwargs.get("channels", "")


class Channel(ICDElement):
    """Generic class for channels"""

    def __init__(self, dict_index, **kwargs):
        ICDElement.__init__(self, dict_index, **kwargs)
        self._type = kwargs.get("type", "")
        self._type_changed = kwargs.get("typeChanged", "")

        self.datas = kwargs.get("datas", "")
        self.data_containers = []

    def get_type(self):
        return self._type

    def get_type_changed(self):
        return self._type_changed


class DataContainer(ICDElement):
    """Generic class for containers"""

    def __init__(self, dict_index, **kwargs):
        ICDElement.__init__(self, dict_index, **kwargs)
        self._type = kwargs.get("type", "")
        #Datacount is useless
        #self._data_count = kwargs.get("dataCount", 0)

        self.datas = kwargs.get("datas", "")
        self.attributes = []
        self.data_containers = []

    def get_type(self):
        return self._type

    #def get_data_count(self):
    #    return self._data_count


class DataContainerAttribute(object):
    """Generic class for containers"""

    def __init__(self, **kwargs):
        self._name = kwargs.get("name", "")
        self._type = kwargs.get("type", "")
        self._value = kwargs.get("value", "")
        self._default_value = kwargs.get("defaultValue", "")
        self._value_pattern = kwargs.get("valuePattern", "")


    def get_type(self):
        return self._type

    def get_name(self):
        return self._name

    def get_value(self):
        return self._value

    def get_default_value(self):
        return self._default_value

    def get_value_pattern(self):
        return self._value_pattern


class Data(ICDElement):
    """Generic class for datas"""

    def __init__(self, dict_index, **kwargs):
        ICDElement.__init__(self, dict_index, **kwargs)
        self._type = kwargs.get("type", "")
        self._size = kwargs.get("size", 0)
        self._size_format = kwargs.get("sizeFormat", "")
        self._min = kwargs.get("min", "")
        self._min_format = kwargs.get("minFormat", "")
        self._max = kwargs.get("max", "")
        self._max_format = kwargs.get("maxFormat", "")
        self._default_value = kwargs.get("defaultValue", "")
        self._default_value_format = kwargs.get("defaultValueFormat", "")
        self._unit = kwargs.get("unit", "")
        self._type_changed = kwargs.get("typeChanged", False)

        self.filters = kwargs.get("filters", "")
        self.datas = kwargs.get("datas", "")
        self.enum_elements = []
        self.channel_types = []
        self.metadatas = []

    def get_type(self):
        return self._type

    def get_size(self):
        return self._size

    def get_size_format(self):
        return self._size_format

    def get_min(self):
        return self._min

    def get_min_format(self):
        return self._min_format

    def get_max(self):
        return self._max

    def get_max_format(self):
        return self._max_format

    def get_default_value(self):
        return self._default_value

    def get_default_value_format(self):
        return self._default_value_format

    def get_unit(self):
        return self._unit

    def get_type_changed(self):
        return self._type_changed


class EnumElement(object):
    def __init__(self, **kwargs):
        self._property = kwargs.get("property", "")
        self._value = kwargs.get("value", "")
        self._type = kwargs.get("type", "")
        self._comment = kwargs.get("comment", "")
        self._value_pattern = kwargs.get("valuePattern", "")
        self._type_changed = kwargs.get("typeChanged", False)

    def get_property(self):
        return self._property

    def get_value(self):
        return self._value

    def get_type(self):
        return self._type

    def get_comment(self):
        return self._comment

    def get_value_pattern(self):
        return self._value_pattern

    def get_type_changed(self):
        return self._type_changed


class DataFilter(ICDElement):
    """Generic class for filters and codecs"""

    def __init__(self, dict_index, **kwargs):
        ICDElement.__init__(self, dict_index, **kwargs)
        self._sequence = kwargs.get("sequence", 0)
        self._sequence_format = kwargs.get("sequenceFormat", "")
        self._type = kwargs.get("type", "")

        self.channel_types = []

    def get_sequence(self):
        return self._sequence

    def get_sequence_format(self):
        return self._sequence_format

    def get_type(self):
        return self._type


class Metadata(object):
    def __init__(self, **kwargs):
        self._key = kwargs.get("key", "")
        self._value = kwargs.get("value", "")

    def get_key(self):
        return self._key

    def get_value(self):
        return self._value
