from s.utest.pyicd.parser import ICDParser
from s.utest.pyicd.pyICD import Data, DataContainer, Channel, DataContainerAttribute, DataFilter
import optparse
import logging

logger = logging.getLogger("ICDDump-ICD")

class ICDDumper(object):
    """Base class for ICD comparison"""
    def __init__(self, icd1, options):
        self.options = options
        self._icd = icd1
        if not options.ignore_order:
            raise ValueError("Preserving order not implemented, keep ignore_order option")
        if not options.ignore_index:
            raise ValueError("Preserving order not implemented, keep ignore_order option")

        self.ip1 = ICDParser(icd1)

    def ignore(self, attr, o=None):
        """Comparison condition
        Args:
            attr: pyICD attribute name
        Returns: True if this attribute is ignored for this comparison
        """
        
        #check if attribute name does not begins with _
        #by convention in pyICD list attributes do not start with _
        res = (attr[0] != "_")

        #The _property tag is ignored because property name already displayed in iterate attributes
        res = res or (attr == "_property")

        #The _name tag is ignored because property name already displayed in iterate_elements
        res = res or (attr == "_name")
        if self.options.ignore_type_changed:
            res = res or (attr == "_type_changed")
        if self.options.ignore_index:
            res = res or (attr == "_index")
        if self.options.ignore_empty:
            if not o is None:
                v = getattr(o,attr)
                if v is None:
                    v = ''
                if v == '' : 
                    logger.debug("ignore empty {} = {}".format (attr,getattr(o,attr)))
                res = res or (v == '')                        
        return res

    def iterate_attributes(self, parent_path, o1, result):
        keys = o1.__dict__.keys()
        keys = list(o1.__dict__.keys())
        keys.sort()

        for attr in keys:
            if not self.ignore(attr,o1):
                if getattr(o1,attr) is None:
                    v=""
                else:
                    v=getattr(o1,attr)
                #remove "_" character
                a=''.join(attr.split('_', 1))
                current_path = parent_path + "/" + a + ":{}".format(v)
                logger.debug(f'iterate_attributes {current_path}')
                result[current_path] = getattr(o1, attr)

        if hasattr(o1, "configs"):
            dict1= {}
            for p in o1.configs:
                dict1[getattr(p, "_property")] = p
            for k in dict1:
                result = self.iterate_attributes(parent_path + "/Config/" + k, dict1[k], result)
        
        if hasattr(o1, "enum_elements"):
            dict1= {}
            for p in o1.enum_elements:
                dict1[getattr(p, "_property")] = p
            for k in dict1:
                result = self.iterate_attributes(parent_path + "/Enum/" + k, dict1[k], result)

        return result
           
    def iterate_elements(self, parent_path, obj, result):
        """Recursively iterate elements to a dictionary
        Args:
            parent_path: parent of 'obj' path
            obj: used pyICD object
            result: dictionary to update

        Returns:
        """
        current_path = parent_path + "/" + obj.get_name()
        result[current_path] = obj
        logger.debug(f"iterate_elements {current_path} ({type(obj)})")

        result = self.iterate_attributes(current_path, obj, result)

        if type(obj) == Channel:
            # Do not iterate datas referenced in the Channel
            #for data in obj.datas:
            #    result = self.iterate_elements(current_path, data, result)

            for container in obj.data_containers:
                result = self.iterate_elements(current_path, container, result)

        if type(obj) in [Data, DataContainer]:
            for data in obj.datas:
                result = self.iterate_elements(current_path, data, result)

        if type(obj) == Data:
            if hasattr(obj, "filters"):
                for dfilter in obj.filters:
                    result = self.iterate_elements(current_path, dfilter, result)      

        elif type(obj) == DataContainer:
            for container_attr in obj.attributes:
                result = self.iterate_elements(current_path+"/", container_attr, result)

            for container in obj.data_containers:
                result = self.iterate_elements(current_path, container, result)

        return result

    def dump(self):
        """Dump the whole ICD
        Args:
        Returns: dict1 parsed icds as paths dictionaries
        """
        logger.info(f'Dumping {self._icd}')

        # convert pyICD to dictionaries to avoid false diffs from xml nodes order differences
        result = {}
        for device in self.ip1.icd.devices:
            device_path = device.get_name()
            result[device_path] = device
            logger.info(f'Dump {device_path} ({type(device)})')
            result = self.iterate_attributes(device_path, device, result)

            for ch in device.channels:
                result = self.iterate_elements(device_path, ch, result)
        
        sorted_r = list(result.keys())
        sorted_r.sort()
        for key in sorted_r:
            print(key)


if __name__ == "__main__":
    # Options management
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-o', '--ignore-order',
                          help='ignore orders of elements, except Filter',
                          action='store_false',
                          dest='ignore_order',
                          default=True)
    opt_parser.add_option('-i', '--ignore-index',
                          help='ignore index value',
                          action='store_false',
                          dest='ignore_index',
                          default=True)
    opt_parser.add_option('-t', '--ignore-type',
                          help='ignore type changed',
                          action='store_false',
                          dest='ignore_type_changed',
                          default=True)                          
    opt_parser.add_option('-e', '--ignore-empty',
                          help='ignore empty attributes in dump',
                          action='store_true',
                          dest='ignore_empty',
                          default=False)                          
    opt_parser.add_option('-l', '--log-level',
                          dest="loglevel",
                          default="WARNING")
    opt_parser.add_option('--log-file',
                          dest="logfile",
                          default=None)

    options, args = opt_parser.parse_args()

    # assuming loglevel is bound to the string value obtained from the
    # command line argument. Convert to upper case to allow the user to
    # specify --log=DEBUG or --log=debug
    loglevel = options.loglevel.upper().strip()

    numeric_level = getattr(logging, loglevel, None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % options.loglevel)

    # log in a file
    logging.basicConfig(level=numeric_level)

    if options.logfile is not None:
        handler = logging.FileHandler(options.logfile)
        handler.setLevel(numeric_level)
        logger.addHandler(handler)

    c = ICDDumper(args[0], options)
    c.dump()            
            
        


