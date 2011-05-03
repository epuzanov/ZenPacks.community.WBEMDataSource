
import Globals
import os.path

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
from Products.CMFCore.DirectoryView import registerDirectory
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())

from Products.ZenModel.ZenPack import ZenPackBase

class ZenPack(ZenPackBase):
    """ WBEMDataSource loader
    """
    packZProperties = [
            ('zWbemMonitorIgnore', True, 'boolean'),
            ('zWbemPort', '5989', 'string'),
            ('zWbemProxy', '', 'string'),
            ('zWbemUseSSL', True, 'boolean'),
            ]
