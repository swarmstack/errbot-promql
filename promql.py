import decimal
import json
import requests
import urllib.parse
from errbot import BotPlugin, botcmd, ValidationException

class PromQL(BotPlugin):
    """
    Query Prometheus via it's API
    """

    def get_configuration_template(self):
        return {'PROMQL_URL': 'http://tasks.prometheus:9090/api/v1'}

    @botcmd
    def promql(self, msg, args):
        """query  Execute a PromQL query against Prometheus and return pretty json results"""
        try:
            req = requests.get('%s/query?query=%s' % (self.config['PROMQL_URL'], urllib.parse.quote_plus(args)))
            if req.status_code == 200:
                str1 = json.dumps(req.json(), indent=4)
                return "\t%s" % str1.replace('    ','\t')
                #return "\t```%s```" % pprint.pformat(req.json(),indent=1)
            else:
                return "got a non-200 response from %s" % req.url
        except ValidationException as exc:
            return 'failed to perform promql query: %s with exception: %s' % (args, exc)

    @botcmd
    def promql_alerts(self, msg, args):
        """Current alert counts from Prometheus"""
        try:
            req = requests.get('%s/query?query=alertmanager_alerts' % (self.config['PROMQL_URL']))
            if req.status_code == 200:
                req = req.json()
                for i in req['data']['result']:
                    yield "Instance: %s - %s: %s" % (i['metric']['job'], i['metric']['state'], str(i['value'][-1:]).replace('[\'','').replace('\']',''))
                return
            else:
                return "got a non-200 response from %s" % req.url
        except ValidationException as exc:
            return 'failed to perform promql_alerts with exception: %s' % exc

    @botcmd
    def promql_cpu(self, msg, args):
        """Current averaged CPU metrics of all or partial host via NetData from Prometheus"""
        try:
            str1 = 'avg(netdata_cpu_cpu_percentage_average{instance=~".*%s.*"}) by (dimension)' % args.strip()
            req = requests.get('%s/query?query=%s' % (self.config['PROMQL_URL'], urllib.parse.quote_plus(str1)))
            if req.status_code == 200:
                req = req.json()
                for i in req['data']['result']:
                    value = decimal.Decimal(str(i['value'][-1:]).replace('[\'','').replace('\']','')).quantize(decimal.Decimal(10) ** -2)
                    yield "CPU %s: %s%%" % ( str(i['metric']['dimension']), value) 
                return
            else:
                return "got a non-200 response from %s" % req.url
        except ValidationException as exc:
            return 'failed to perform promql_cpu with args %s, exception: %s' % (args, exc)

    @botcmd
    def promql_cpufree(self, msg, args):
        """Current free CPU of all or partial host via NetData from Prometheus"""
        try:
            str1 = 'avg(netdata_cpu_cpu_percentage_average{dimension="idle",instance=~".*%s.*"}) by (instance)' % args.strip()
            req = requests.get('%s/query?query=%s' % (self.config['PROMQL_URL'], urllib.parse.quote_plus(str1)))
            if req.status_code == 200:
                req = req.json()
                for i in req['data']['result']:
                    cpuidle = decimal.Decimal(str(i['value'][-1:]).replace('[\'','').replace('\']','')).quantize(decimal.Decimal(10) ** -1)
                    yield "Host: %s: %s%% cpu idle" % ( str(i['metric']['instance']), cpuidle) 
                return
            else:
                return "got a non-200 response from %s" % req.url
        except ValidationException as exc:
            return 'failed to perform promql_cpufree with args %s, exception: %s' % (args, exc)

    def lowestcpufree(self):
        """Current lowest free CPU host via NetData from Prometheus"""
        try:
            req = requests.get('%s/query?query=%s' % (self.config['PROMQL_URL'], urllib.parse.quote_plus('bottomk(1, avg(netdata_cpu_cpu_percentage_average{dimension="idle"}) by (instance) )')))
            if req.status_code == 200:
                req = req.json()
                for i in req['data']['result']:
                    cpuidle = decimal.Decimal(str(i['value'][-1:]).replace('[\'','').replace('\']','')).quantize(decimal.Decimal(10) ** -1)
                    return "Host: %s: %s%% cpu idle" % ( str(i['metric']['instance']), cpuidle) 
                return
            else:
                return "got a non-200 response from %s" % req.url
        except ValidationException as exc:
            return 'failed to perform promql query with exception: %s' % exc

    def lowestmemfree(self):
        """Current lowest free memory NetData from Prometheus"""
        try:
            req = requests.get('%s/query?query=%s' % (self.config['PROMQL_URL'], urllib.parse.quote_plus('floor( bottomk(1, 100 / sum(netdata_system_ram_MiB_average) by (instance) * sum(netdata_system_ram_MiB_average{dimension=~"free|cached"} ) by (instance) ) )')))
            if req.status_code == 200:
                req = req.json()
                for i in req['data']['result']:
                    str1 = 'netdata_mem_available_MiB_average{instance="%s"}' % i['metric']['instance']
                    req2 = requests.get('%s/query?query=%s' % (self.config['PROMQL_URL'], urllib.parse.quote_plus(str1)))
                    if req2.status_code == 200:
                        req2 = req2.json()
                        for j in req2['data']['result']:
                            memavail = decimal.Decimal(str(j['value'][-1:]).replace('[\'','').replace('\']','')).quantize(decimal.Decimal(10) ** 0)
                            memavailpercent = str(i['value'][-1:]).replace('[\'','').replace('\']','')
                            return "Host: %s: %sMB (%s%%) memory free/cached" % ( str(i['metric']['instance']), memavail, memavailpercent) 
                    else:
                        return "got a non-200 response from %s" % req2.url
                return
            else:
                return "got a non-200 response from %s" % req.url
        except ValidationException as exc:
            return 'failed to perform promql query with exception: %s' % exc

    def lowestrootfree(self):
        """Current lowest free root filesystem via NetData from Prometheus"""
        try:
            req = requests.get('%s/query?query=%s' % (self.config['PROMQL_URL'], urllib.parse.quote_plus('floor( bottomk(1, 100 / sum(netdata_disk_space_GiB_average{family="/"}) by (instance) * sum(netdata_disk_space_GiB_average{family="/",dimension="avail"} ) by (instance) ) )')))
            if req.status_code == 200:
                req = req.json()
                for i in req['data']['result']:
                    str1 = 'netdata_disk_space_GiB_average{instance="%s", family="/", dimension="avail"}' % i['metric']['instance']
                    req2 = requests.get('%s/query?query=%s' % (self.config['PROMQL_URL'], urllib.parse.quote_plus(str1)))
                    if req2.status_code == 200:
                        req2 = req2.json()
                        for j in req2['data']['result']:
                            diskavail = decimal.Decimal(str(j['value'][-1:]).replace('[\'','').replace('\']','')).quantize(decimal.Decimal(10) ** -1)
                            diskavailpercent = str(i['value'][-1:]).replace('[\'','').replace('\']','')
                            return "Host: %s: %sGB (%s%%) root filesystem free" % ( str(i['metric']['instance']), diskavail, diskavailpercent) 
                    else:
                        return "got a non-200 response from %s" % req2.url
                return
            else:
                return "got a non-200 response from %s" % req.url
        except ValidationException as exc:
            return 'failed to perform promql query with exception: %s' % exc

    @botcmd
    def promql_lowest(self, msg, args):
        """Current lowest free CPU, memory, and root filesystem host via NetData from Prometheus"""
        yield ( f'{self.lowestcpufree()}\n'
                f'{self.lowestmemfree()}\n'
                f'{self.lowestrootfree()}' )
        return

    @botcmd
    def promql_lowestcpufree(self, msg, args):
        """Current lowest free CPU host via NetData from Prometheus"""
        yield ( f'{self.lowestcpufree()}' )
        return

    @botcmd
    def promql_lowestmemfree(self, msg, args):
        """Current lowest free memory host NetData from Prometheus"""
        yield ( f'{self.lowestmemfree()}' )
        return

    @botcmd
    def promql_lowestrootfree(self, msg, args):
        """Current lowest free root filesystem host via NetData from Prometheus"""
        yield ( f'{self.lowestrootfree()}' )
        return

    @botcmd
    def promql_memfree(self, msg, args):
        """Current free memory of all or partial host via NetData from Prometheus"""
        try:
            str1 = 'floor( 100 / sum(netdata_system_ram_MiB_average{instance=~".*%s.*"}) by (instance) * sum(netdata_system_ram_MiB_average{dimension=~"free|cached",instance=~".*%s.*"} ) by (instance) )' % (args.strip(), args.strip())
            req = requests.get('%s/query?query=%s' % (self.config['PROMQL_URL'], urllib.parse.quote_plus(str1)))
            if req.status_code == 200:
                req = req.json()
                for i in req['data']['result']:
                    str1 = 'netdata_mem_available_MiB_average{instance="%s"}' % i['metric']['instance']
                    req2 = requests.get('%s/query?query=%s' % (self.config['PROMQL_URL'], urllib.parse.quote_plus(str1)))
                    if req2.status_code == 200:
                        req2 = req2.json()
                        for j in req2['data']['result']:
                            memavail = decimal.Decimal(str(j['value'][-1:]).replace('[\'','').replace('\']','')).quantize(decimal.Decimal(10) ** 0)
                            memavailpercent = str(i['value'][-1:]).replace('[\'','').replace('\']','')
                            yield "Host: %s: %sMB (%s%%) memory free/cached" % ( str(i['metric']['instance']) , memavail, memavailpercent) 
                    else:
                        return "got a non-200 response from %s" % req2.url
                return
            else:
                return "got a non-200 response from %s" % req.url
        except ValidationException as exc:
            return 'failed to perform promql_cpufree with args %s, exception: %s' % (args, exc)

    @botcmd
    def promql_raw(self, msg, args):
        """query  Execute a PromQL query against Prometheus and return raw json results"""
        try:
            req = requests.get('%s/query?query=%s' % (self.config['PROMQL_URL'], urllib.parse.quote_plus(args)))
            if req.status_code == 200:
                return req.json()
            else:
                return "got a non-200 response from %s" % req.url
        except ValidationException as exc:
            return 'failed to perform promql query: %s with exception: %s' % (args, exc)

    @botcmd
    def promql_rootfree(self, msg, args):
        """Current free root filesystem of all or partial host via NetData from Prometheus"""
        try:
            str1 = 'floor( 100 / sum(netdata_disk_space_GiB_average{family="/",instance=~".*%s.*"}) by (instance) * sum(netdata_disk_space_GiB_average{family="/",dimension="avail",instance=~".*%s.*"} ) by (instance) )' % (args.strip(), args.strip())
            req = requests.get('%s/query?query=%s' % (self.config['PROMQL_URL'], urllib.parse.quote_plus(str1)))
            if req.status_code == 200:
                req = req.json()
                for i in req['data']['result']:
                    str1 = 'netdata_disk_space_GiB_average{instance="%s", family="/", dimension="avail"}' % i['metric']['instance']
                    req2 = requests.get('%s/query?query=%s' % (self.config['PROMQL_URL'], urllib.parse.quote_plus(str1)))
                    if req2.status_code == 200:
                        req2 = req2.json()
                        for j in req2['data']['result']:
                            diskavail = decimal.Decimal(str(j['value'][-1:]).replace('[\'','').replace('\']','')).quantize(decimal.Decimal(10) ** -1)
                            diskavailpercent = str(i['value'][-1:]).replace('[\'','').replace('\']','')
                            yield "Host: %s: %sGB (%s%%) root filesystem free" % (str(i['metric']['instance']), diskavail, diskavailpercent) 
                    else:
                        return "got a non-200 response from %s" % req2.url
                return
            else:
                return "got a non-200 response from %s" % req.url
        except ValidationException as exc:
            return 'failed to perform promql_rootfree with exception: %s' % exc


#promql alertcounts
# alertmanager_alerts
# {
#    'status':'success',
#    'data':{
#       'resultType':'vector',
#       'result':[
#          {
#             'metric':{
#                'name':'alertmanager_alerts',
#                'instance':'10.0.6.54:9093',
#                'job':'alertmanagerB',
#                'state':'active'
#             },
#             'value':[
#                1540325675.084,
#                '0'
#             ]
#          },
#          {
#             'metric':{
#                'name':'alertmanager_alerts',
#                'instance':'10.0.6.54:9093',
#                'job':'alertmanagerB',
#                'state':'suppressed'
#             },
#             'value':[
#                1540325675.084,
#                '3'
#             ]
#          },
#          {
#             'metric':{
#                'name':'alertmanager_alerts',
#                'instance':'10.0.6.76:9093',
#                'job':'alertmanager',
#                'state':'active'
#             },
#             'value':[
#                1540325675.084,
#                '0'
#             ]
#          },
#          {
#             'metric':{
#                'name':'alertmanager_alerts',
#                'instance':'10.0.6.76:9093',
#                'job':'alertmanager',
#                'state':'suppressed'
#             },
#             'value':[
#                1540325675.084,
#                '3'
#             ]
#          }
#       ]
#    }
# }

#promql lowestroot
# floor( bottomk(1, 100 / sum(netdata_disk_space_GiB_average{family="/"}) by (job) * sum(netdata_disk_space_GiB_average{family="/",dimension="avail"} ) by (job) ) )
# {
#    'status':'success',
#    'data':{
#       'resultType':'vector',
#       'result':[
#          {
#             'metric':{
#                'instance':'swarm02.example.com'
#             },
#             'value':[
#                1540398950.395,
#                '22'
#             ]
#          }
#       ]
#    }
# }


#promql cpu host
# avg(netdata_cpu_cpu_percentage_average{instance=~".*HOSTNAME.*"}) by (dimension)
# {
#    'status':'success',
#    'data':{
#       'resultType':'vector',
#       'result':[
#          {
#             'metric':{
#                'dimension':'iowait'
#             },
#             'value':[
#                1540407519.45,
#                '0'
#             ]
#          },
#          {
#             'metric':{
#                'dimension':'user'
#             },
#             'value':[
#                1540407519.45,
#                '0.8117895125000001'
#             ]
#          },
#          {
#             'metric':{
#                'dimension':'guest'
#             },
#             'value':[
#                1540407519.45,
#                '0'
#             ]
#          },
#          {
#             'metric':{
#                'dimension':'idle'
#             },
#             'value':[
#                1540407519.45,
#                '98.1336502625'
#             ]
#          },
#          {
#             'metric':{
#                'dimension':'irq'
#             },
#             'value':[
#                1540407519.45,
#                '0'
#             ]
#          },
#          {
#             'metric':{
#                'dimension':'nice'
#             },
#             'value':[
#                1540407519.45,
#                '0'
#             ]
#          },
#          {
#             'metric':{
#                'dimension':'softirq'
#             },
#             'value':[
#                1540407519.45,
#                '0.008250825'
#             ]
#          },
#          {
#             'metric':{
#                'dimension':'steal'
#             },
#             'value':[
#                1540407519.45,
#                '0'
#             ]
#          },
#          {
#             'metric':{
#                'dimension':'system'
#             },
#             'value':[
#                1540407519.45,
#                '1.046309825'
#             ]
#          },
#          {
#             'metric':{
#                'dimension':'guest_nice'
#             },
#             'value':[
#                1540407519.45,
#                '0'
#             ]
#          }
#       ]
#    }
# }
