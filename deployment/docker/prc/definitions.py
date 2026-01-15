import json
import requests
from mysql_conf import *
from playhouse.shortcuts import model_to_dict, dict_to_model
from pint        import UnitRegistry
from kubernetes import client,config

ureg = UnitRegistry()

# Memory units
ureg.define('kmemunits = 1 = [kmemunits]')
ureg.define('Ki = 1024 * kmemunits')
ureg.define('Mi = Ki^2')
ureg.define('Gi = Ki^3')
ureg.define('Ti = Ki^4')
ureg.define('Pi = Ki^5')
ureg.define('Ei = Ki^6')

# cpu units
ureg.define('kcpuunits = 1 = [kcpuunits]')
ureg.define('n = 1/1000000000 * kcpuunits')
ureg.define('u = 1/1000000 * kcpuunits')
ureg.define('m = 1/1000 * kcpuunits')
ureg.define('k = 1000 * kcpuunits')
ureg.define('M = k^2')
ureg.define('G = k^3')
ureg.define('T = k^4')
ureg.define('P = k^5')
ureg.define('E = k^6')

Q_ = ureg.Quantity

def getServiceComponents():
  query = (serviceComponent.select(serviceComponent.id,serviceComponent.service_id,service.name.alias('service_name'),serviceComponent.name).join(service)).dicts()
  dict = []
  print(query)
  for q in query:
      print('service component element: ', q)
      dict.append(q)
  return dict

def getMetrics():
  config.load_incluster_config()
  cust = client.CustomObjectsApi()
  dict = cust.list_namespaced_custom_object('metrics.k8s.io', 'v1beta1', 'default', 'pods')
  return dict

def getResources(comp, metrics):
  cpu = 0
  ram = 0
  service = comp['service_name']
  component = comp['name']
  for item in metrics['items']:
    if not (('labels' in item['metadata']) and ('service' in item['metadata']['labels'] and 'app.kubernetes.io/servicecomponent' in item['metadata']['labels'])):
      continue
    mservice = item['metadata']['labels']['service']
    mserviceComponent = item['metadata']['labels']['app.kubernetes.io/servicecomponent']
    if mservice == service and mserviceComponent == component:
      for container in item['containers']:
        mcpu = int(Q_(container['usage']['cpu']).to('m').magnitude)
        mram = int(Q_(container['usage']['memory']).to('Mi').magnitude)
        cpu += mcpu
        ram += mram
  return cpu, ram

def setMetrics(values):
  for val in values:
    try:
      f = data.get(
      (data.service_id == val['service_id']) &
      (data.servicecomponent_id == val['servicecomponent_id']) &
      (data.timestamp == val['timestamp']))
    except data.DoesNotExist:
      data.create(**val)
      continue
    up = data.update(**val).where(
      data.service_id==val['service_id'],
      data.servicecomponent_id==val['servicecomponent_id'],
      data.timestamp==val['timestamp'],
      data.real == 0
    ).execute()
