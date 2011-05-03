################################################################################
#
# This program is part of the WBEMDataSource Zenpack for Zenoss.
# Copyright (C) 2009, 2010, 2011 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""WBEMDataSource

Defines attributes for how a datasource will be graphed
and builds the nessesary DEF and CDEF statements for it.

$Id: WBEMDataSource.py,v 2.0 2011/05/03 23:00:09 egor Exp $"""

__version__ = "$Revision: 2.0 $"[11:-2]

from Products.ZenModel.RRDDataSource import RRDDataSource
from ZenPacks.community.SQLDataSource.datasources import SQLDataSource
from AccessControl import ClassSecurityInfo, Permissions

import re
PATHPAT = re.compile("^(?:([^\. ]+):)?([^\.\: ]+)(?:\.(.+))?", re.I)
CSTMPL = "'pywbemdb',scheme='%s',port=%s,user='%s',password='%s',host='%s',namespace='%s'"

class WBEMDataSource(SQLDataSource.SQLDataSource):

    ZENPACKID = 'ZenPacks.community.WBEMDataSource'

    sourcetypes = ('WBEM',)
    sourcetype = 'WBEM'
    namespace = 'root/cimv2'
    instance = ''

    _properties = RRDDataSource._properties + (
        {'id':'namespace', 'type':'string', 'mode':'w'},
        {'id':'instance', 'type':'string', 'mode':'w'},
        )


    # Screen action bindings (and tab definitions)
    factory_type_information = (
    {
        'immediate_view' : 'editWBEMDataSource',
        'actions'        :
        ( 
            { 'id'            : 'edit'
            , 'name'          : 'Data Source'
            , 'action'        : 'editWBEMDataSource'
            , 'permissions'   : ( Permissions.view, )
            },
        )
    },
    )


    def getDescription(self):
        return self.instance


    def zmanage_editProperties(self, REQUEST=None):
        'add some validation'
        if REQUEST:
            self.namespace = REQUEST.get('namespace', '')
            self.instance = REQUEST.get('instance', '')
        return RRDDataSource.zmanage_editProperties(self, REQUEST)


    def getConnectionString(self, context, namespace=''):
        if not namespace: namespace = self.getCommand(context, self.namespace)
        if hasattr(context, 'device'):
            device = context.device()
        else:
            device = context
        scheme = getattr(device, 'zWbemUseSSL', False) and 'https' or 'http'
        port = int(getattr(device, 'zWbemPort', 5989))
        user = getattr(device, 'zWinUser', '')
        password = getattr(device, 'zWinPassword', '')
        host = getattr(device,'zWbemProxy','') or getattr(device,'manageIp','')
        return CSTMPL%(scheme, port, user, password, host, namespace)


    def getQueryInfo(self, context):
        try:
            sql = self.getCommand(context,self.instance.encode('string-escape'))
            if sql.upper().startswith('SELECT '):
                sqlp, kbs = self.parseSqlQuery(sql)
                return sql, sqlp, kbs, self.getConnectionString(context)
            namespace, classname, where = PATHPAT.match(sql).groups('')
            cs = self.getConnectionString(context, namespace)
            cols=','.join([dp.getAliasNames() and dp.getAliasNames()[0] or dp.id \
                                for dp in self.getRRDDataPoints()] or ['*'])
            kbs = eval('(lambda **kws:kws)(%s)'%where.encode('string-escape'))
            if kbs and cols != '*': cols = cols + ',' + ','.join(kbs.keys())
            if where:
                where = ' WHERE ' + where.replace(',',' AND ')
            sqlp = 'SELECT %s FROM %s'%(cols, classname)
            return sqlp + where, sqlp, kbs, cs
        except:
            return '', '', {}, ''
