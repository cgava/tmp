from distutils.debug import DEBUG
import logging
import xml.etree.ElementTree as ET
import sys

from attr import has
from s.utest.pyicd.pyICD import ICD, Bus, Device, Channel,\
    Data, DataContainer, DataContainerAttribute,\
    DataFilter, Config, Metadata, EnumElement

logger = logging.getLogger("ate2009-ICD-parser")

def split_paths(value):
    """Convert a string from ATE into a list of list of strings
    Args:
        value: string representing a list of ICD path, for example:
                '//@bus/@filters.0 //@bus/@filters.1'

    Returns: list of list of strings
    """
    path_list = value.split(" ")
    res = []
    for path in path_list:
        v = path.replace("@", "")[1:].split("/")
        res.append(v[1:])
    return res


class ICDParser(object):
    """Read an ate file as an xml file and parse it as pyICD object"""

    def __init__(self, icd_path):
        self.xml_root = None
        self._icd_path = icd_path

        self.to_update = []
        self.icd=self.eval()

    def parse_refs(self, path):
        """Get pyICD object traveling through the given path.
        Args:
            path: list of icd elements name to travel through
        Returns: pyICD object at the given path
        """
        if path:
            current_object = self._icd
            for attr in path:
                attr_name = attr
                if "." in attr:  # for example //@bus/@filters.1 is the second filter
                    attr_name, index = tuple(attr.split("."))
                # get attribute
                current_object = getattr(current_object, attr_name)
                if "." in attr:  # for a list get element at specified index
                    current_object = current_object[int(index)]
            return current_object
        return None

    def parse_device(self, xml_device):
        """Parse a device from a xml node
        Args:
            xml_device: xml device node
        Returns: pyICD Device object
        """
        res = Device(self._icd.dict_index,**xml_device.attrib)
        res.channels = split_paths(res.channels)
        self.to_update.append({"obj": res, "attr": "channels"})
        return res

    def parse_bus(self, xml_bus):
        """Parse a bus from a xml node
        Args:
            xml_bus: xml bus node
        Returns: pyICD Bus object
        """
        res = Bus()
        for child in xml_bus:
            logger.debug(f"parse_bus adding {child.tag} {child.attrib}")
            if child.tag == "channels":
                ch = self.parse_channel(child)
                res.channels.append(ch)
            elif child.tag == "datas":
                ch = self.parse_data(child)
                res.datas.append(ch)
            elif child.tag == "filters":
                ch = self.parse_filter(child)
                res.filters.append(ch)
            else:
                msg = "Unknown tag '{}' for bus".format(child.tag)
                logger.warn(msg)
        return res

    @staticmethod
    def parse_config(xml_conf):
        res = Config(**xml_conf.attrib)
        return res

    def parse_channel(self, xml_channel):
        """Parse a channel from a xml node
        Args:
            xml_channel: xml channel node
        Returns: pyICD Channel object
        """
        res = Channel(self._icd.dict_index, **xml_channel.attrib)
        res.datas = split_paths(res.datas)
        self.to_update.append({"obj": res, "attr": "datas"})
        for child in xml_channel:
            logger.debug(f"parse_channel adding {child.tag} {child.attrib}")
            if child.tag == "parents":
                res.parents.append(child.text)
            elif child.tag == "configs":
                conf = self.parse_config(child)
                res.configs.append(conf)
            elif child.tag == "dataContainers":
                cont = self.parse_data_container(child)
                res.data_containers.append(cont)
            elif child.tag == "datas":
                ch = self.parse_data(child)
                res.datas.append(ch)
            else:
                msg = "Unknown tag '{}' for channel".format(child.tag)
                logger.warn(msg)
        return res

    def parse_data_container(self, xml_cont):
        """Parse a data container from a xml node
        Args:
            xml_cont: xml data container node
        Returns: pyICD DataContainer object
        """
        res = DataContainer(self._icd.dict_index,**xml_cont.attrib)
        res.datas = split_paths(res.datas)
        self.to_update.append({"obj": res, "attr": "datas"})
        for child in xml_cont:
            logger.debug(f"parse_data_container adding {child.tag} {child.attrib}")
            if child.tag == "parents":
                res.parents.append(child.text)
            elif child.tag == "configs":
                conf = self.parse_config(child)
                res.configs.append(conf)
            elif child.tag == "sublists":
                cont = self.parse_data_container(child)
                res.data_containers.append(cont)
            elif child.tag == "datas":
                ch = self.parse_data(child)
                res.datas.append(ch)
            elif child.tag == "attributes":
                a = self.parse_attribute(child)
                res.attributes.append(a)
            else:
                msg = "Unknown tag '{}' for data container".format(child.tag)
                logger.warn(msg)
        return res

    @staticmethod
    def parse_attribute(xml_attr):
        """Parse an attribute from a xml node
        Args:
            xml_attr: xml attribute node
        Returns: pyICD DataContainerAttribute object
        """
        res = DataContainerAttribute(**xml_attr.attrib)
        return res

    def parse_data(self, xml_data):
        """Parse a data from a xml node
        Args:
            xml_data: xml data node
        Returns: pyICD Data object
        """
        res = Data(self._icd.dict_index,**xml_data.attrib)
        res.filters = split_paths(res.filters)
        res.datas = split_paths(res.datas)
        self.to_update.append({"obj": res, "attr": "filters"})
        self.to_update.append({"obj": res, "attr": "datas"})
        for child in xml_data:
            logger.debug(f"parse_data adding {child.tag} {child.attrib}")
            if child.tag == "parents":
                res.parents.append(child.text)
            elif child.tag == "channelTypes":
                res.channel_types.append(child.text)
            elif child.tag == "metadatas":
                md = self.parse_metadata(child)
                res.metadatas.append(md)
            elif child.tag == "configs":
                conf = self.parse_config(child)
                res.configs.append(conf)
            elif child.tag == "parents":
                res.parents.append(child.text)
            elif child.tag == "datas":
                ch = self.parse_data(child)
                res.datas.append(ch)
            elif child.tag == "filters":
                f = self.parse_filter(child)
                res.filters.append(f)
            elif child.tag == "enumElements":
                ee = EnumElement(**child.attrib)
                res.enum_elements.append(ee)
            else:
                msg = "Unknown tag '{}' for data".format(child.tag)
                logger.warn(msg)
        return res

    def parse_filter(self, xml_filter):
        """Parse a filter from a xml node
        Args:
            xml_filter: xml filter node
        Returns: pyICD DataFilter object
        """
        res = DataFilter(self._icd.dict_index, **xml_filter.attrib)
        for child in xml_filter:
            logger.debug(f"parse_data adding {child.tag} {child.attrib}")
            if child.tag == "configs":
                conf = self.parse_config(child)
                res.configs.append(conf)
            elif child.tag == "channelTypes":
                res.channel_types.append(child.text)
            elif child.tag == "parents":
                res.parents.append(child.text)
            else:
                msg = "Unknown tag '{}' for filter".format(child.tag)
                logger.warn(msg)
        return res

    @staticmethod
    def parse_metadata(xml_metadata):
        """Parse a mata data from a xml node
        Args:
            xml_metadata: xml metadata node
        Returns: pyICD Metadata object
        """
        res = Metadata(**xml_metadata.attrib)
        return res

    def replace_refs(self, refs):
        """
        Args:
            refs:

        Returns:
        """
        tmp = []
        for ref in refs:
            o = self.parse_refs(ref)
            if o is not None:
                tmp.append(o)
        return tmp

    def eval(self):
        """Parse ICD file as a pyICD object
        Returns: ICD python object
        """
        tree = ET.parse(self._icd_path)
        self.xml_root = tree.getroot()

        self._icd = ICD()

        for child in self.xml_root:
            logger.debug(f"eval adding {child.tag} {child.attrib}")
            if child.tag == "devices":
                self._icd.devices.append(self.parse_device(child))
            elif child.tag == "bus":
                self._icd.bus = self.parse_bus(child)
            else:
                msg = "Unknown tag '{}' for ICD".format(child.tag)
                logger.warn(msg)

        # parse all refs
        for i,update in enumerate(self.to_update):
            refs_list = getattr(update["obj"], update["attr"])
            setattr(update["obj"], update["attr"], self.replace_refs(refs_list))

        return self._icd

if __name__ == "__main__":
     # log in a file
    logging.basicConfig(level=logging.DEBUG)
    print(f"Parsing {sys.argv[1]}")
    ICDParser(sys.argv[1])