from kubernetes import client, config
from peewee import *
from mysql_conf import *
import json
import requests
from datetime import datetime, timedelta
import json
import yaml

api_port = os.environ['API_PORT']
tm = os.environ['TM_HOST']
tm_port = os.environ['TM_PORT']
im = os.environ['IM_HOST']
im_port = os.environ['IM_PORT']

def version():
    headers = ['service','version']
    data = [os.environ['SERVICE_NAME'],os.environ['SERVICE_VERSION']]
    return dict(zip(headers,data))

def health():
    health_status = True
    if (requests.get('http://{}:{}/health'.format(tm,tm_port)).status_code != 200 or
        requests.get('http://{}:{}/health'.format(im,im_port)).status_code != 200 ):
        health_status = False
    return health_status

def apiexport():
    f = open('openapi.yaml')
    data = yaml.load(f, Loader=yaml.Loader)
    return data

def createTables():
    service.create_table()
    serviceComponent.create_table()
    data.create_table()

def core_v1():
    config.load_incluster_config()
    return client.CoreV1Api()

def apps_v1():
    config.load_incluster_config()
    return client.AppsV1Api()

def getMetrics():
    config.load_incluster_config()
    cust = client.CustomObjectsApi()
    dict = cust.list_namespaced_custom_object(
        'metrics.k8s.io', 'v1beta1', 'default', 'pods')
    return dict

def getServices():
    pods = core_v1().list_namespaced_pod(namespace='default')
    services = []
    for item in pods.items:
        if 'service' in item.metadata.labels:
            service = item.metadata.labels['service']
            if not service in services:
                services.append(service)
    return services

def getServiceComponents(service):
    pods = core_v1().list_namespaced_pod(namespace='default')
    serviceComponents = []
    for item in pods.items:
        if 'service' in item.metadata.labels and service == item.metadata.labels['service']:
            if 'app.kubernetes.io/servicecomponent' in item.metadata.labels and not item.metadata.labels['app.kubernetes.io/servicecomponent'] in serviceComponents:
                serviceComponent = item.metadata.labels['app.kubernetes.io/servicecomponent']
                serviceComponents.append(serviceComponent)
    return serviceComponents

def getDeployments(service):
    deploy = apps_v1().list_namespaced_deployment(namespace='default')
    deployments = []
    for item in deploy.items:
        if 'service' in item.metadata.labels and service == item.metadata.labels['service']:
            if 'app.kubernetes.io/servicecomponent' in item.metadata.labels:
                deployments.append(item.metadata.name)
    return deployments

def services():
    services = getServices()
    data = {"services" : []}
    for en in services:
        service = getInferService(en)
        if service is None: continue
        serviceComponents = getServiceComponents(en)
        compList = []
        for comp in serviceComponents:
            serviceComponent = getInferServiceComponent(service.id,comp)
            if serviceComponent is None: continue
            compData = {
                "name": comp,
                "managed": serviceComponent.infer
            }
            compList.append(compData)
        serviceData = {
            "name": en,
            "managed": service.infer,
            "components": compList
        }
        data["services"].append(serviceData)
    return data

def servicespost(jsonData):
    data = json.loads(json.dumps(jsonData))
    keys = dict(data).keys()
    if not 'services' in keys: return 'Invalid JSON'
    for en in data['services']:
        keys = dict(en).keys()
        if not ('name' or 'managed' or 'components') in keys: return 'Invalid JSON'
        if type(en['managed']) is not bool: return 'managed services must be true or false'
        try:
            serviceData = service.get(service.name == en['name'])
        except service.DoesNotExist:
            continue
        if (not en['managed'] and not serviceData.infer): continue
        elif (not en['managed'] and serviceData.infer): serviceVal = {'infer': False}
        else: serviceVal = {'infer': True}
        for comp in en['components']:
            keys = dict(comp).keys()
            if not ('name' or 'managed') in keys: return 'Invalid JSON'
            if type(comp['managed']) is not bool: return 'managed components must be true or false'
            try:
                serviceComponentData = serviceComponent.get((serviceComponent.service_id == serviceData.id) & (serviceComponent.name == comp['name']))
            except serviceComponent.DoesNotExist:
                continue
            if not en['managed']: serviceComponentVal = {'infer': False}
            else: serviceComponentVal = {'infer': comp['managed']}
            up = serviceComponent.update(**serviceComponentVal).where(serviceComponent.service_id==serviceData.id,serviceComponent.name==serviceComponentData.name)
            up.execute()
        up = service.update(**serviceVal).where(service.id==serviceData.id)
        up.execute()
    return 'Services managed updates sucessfully'

def getInferService(e):
    try:
      serviceObject = service.get(service.name == e)
      return serviceObject
    except service.DoesNotExist:
      return None

def getInferServiceComponent(e,c):
    try:
      serviceComponentObject = serviceComponent.get((serviceComponent.service_id == e) & (serviceComponent.name == c))
      return serviceComponentObject
    except serviceComponent.DoesNotExist:
      return None

def addServices():
    services = getServices()
    data = {"services" : []}
    for en in services:
        serviceComponents = getServiceComponents(en)
        compList = []
        for comp in serviceComponents:
            compData = {
                "name": comp,
                "managed": serviceComponent.infer
            }
            compList.append(compData)
        serviceData = {
            "name": en,
            "managed": service.infer,
            "components": compList
        }
        data["services"].append(serviceData)
    for d in data['services']:
        keys = dict(d).keys()
        if 'name' in keys:
            service.get_or_create(name=d['name'])
            id = service.select(service.id).where(
                service.name == d['name']).get()
            if 'components' in keys:
                for comp in d['components']:
                    serviceComponent.get_or_create(
                        service_id=id, name=comp['name'])
    return "Services added or updated sucesfully"

def train():
    url = 'http://{}:{}/train'.format(tm,tm_port)
    data = requests.get(url).text
    return data

def trainvalues():
    url = 'http://{}:{}/train-values'.format(tm,tm_port)
    data = json.loads(json.dumps(requests.get(url).json()))
    return data

def trainvaluespost(json):
    url = 'http://{}:{}/train-values'.format(tm,tm_port)
    data = requests.post(url, json=json).text
    return data

def deleteData():
    curr = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    datadb = curr - timedelta(days=14)
    return 0

def inference():
    data = requests.get('http://{}:{}/inference'.format(im,im_port)).text
    return data