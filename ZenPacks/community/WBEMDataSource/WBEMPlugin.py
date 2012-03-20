################################################################################
#
# This program is part of the WBEMDataSource Zenpack for Zenoss.
# Copyright (C) 2009-2012 Egor Puzanov.
#
# This program can be used under the GNU General Public License version 2
# You can find full information here: http://www.zenoss.com/oss
#
################################################################################

__doc__="""WBEMPlugin

wrapper for SQLPlugin

$Id: WBEMPlugin.py,v 2.1 2012/03/20 20:17:05 egor Exp $"""

__version__ = "$Revision: 2.1 $"[11:-2]

from ZenPacks.community.SQLDataSource.SQLPlugin import SQLPlugin

CSTMPL = "'pywbemdb',scheme='%s',port=%s,user='%s',password='%s',host='%s',namespace='%s'"

class WBEMPlugin(SQLPlugin):
    """
    A WBEMPlugin defines a native Python collection routine and a parsing
    method to turn the returned data structure into a datamap. A valid
    WBEMPlugin must implement the process method.
    """

    deviceProperties = SQLPlugin.deviceProperties + (
        'zWinUser',
        'zWinPassword',
        'zWbemPort',
        'zWbemProxy',
        'zWbemUseSSL',
    )

    def prepareQueries(self, device):
        queries = self.queries(device)
        scheme = getattr(device, 'zWbemUseSSL', False) and 'https' or 'http'
        port = int(getattr(device, 'zWbemPort', 5989))
        user = getattr(device, 'zWinUser', '')
        password = getattr(device, 'zWinPassword', '')
        host = getattr(device,'zWbemProxy','') or getattr(device,'manageIp','')
        for tname, query in queries.iteritems():
            sql, kbs, namespace, columns = query
            if not sql.lower().startswith('select '):
                sql = 'SELECT %s FROM %s'%('*', sql)
                if kbs:
                    kbstrings = []
                    for kbn, kbv in kbs.iteritems():
                        if type(kbv) == str: kbv = '"%s"'%kbv
                        kbstrings.append('%s=%s'%(kbn, kbv))
                    sql = sql + ' WHERE %s'%' AND '.join(kbstrings)
            cs = CSTMPL%(scheme, port, user, password, host, namespace)
            columns = dict(zip(columns.values(), columns.keys()))
            queries[tname] = (sql, kbs, cs, columns)
        return queries
