from mysql_conf import *
import json
import requests
from datetime import datetime,timedelta
from kubernetes import client,config
from pint import UnitRegistry

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
ureg.define('m = 11/1000 * kcpuunits')
ureg.define('k = 1000 * kcpuunits')
ureg.define('M = k^2')
ureg.define('G = k^3')
ureg.define('T = k^4')
ureg.define('P = k^5')
ureg.define('E = k^6')

Q_ = ureg.Quantity

def core_v1():
    config.load_incluster_config()
    return client.CoreV1Api()

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
    components = []
    for item in pods.items:
        if 'service' in item.metadata.labels and service == item.metadata.labels['service']:
            if 'app.kubernetes.io/servicecomponent' in item.metadata.labels and not item.metadata.labels['app.kubernetes.io/servicecomponent'] in components:
                component = item.metadata.labels['app.kubernetes.io/servicecomponent']
                components.append(component)
    return components

def getService(e):
    try:
      serviceObject = service.get(service.name == e)
      return serviceObject
    except service.DoesNotExist:
      return None

def getServiceComponent(e,c):
    try:
      serviceComponentObject = serviceComponent.get((serviceComponent.service_id == e) & (serviceComponent.name == c))
      return serviceComponentObject
    except serviceComponent.DoesNotExist:
      return None

def getDeployments():
	config.load_incluster_config()
	v1 = client.AppsV1Api()
	list_deploy = v1.list_namespaced_deployment(namespace='default')
	list = []
	for deploy in list_deploy.items:
		if not 'service' in deploy.spec.template.metadata.labels:
			continue
		cpu = 0
		ram = 0
		for container in deploy.spec.template.spec.containers:
			if container.resources.requests:
				cpu += int(Q_(container.resources.requests['cpu']).to('m').magnitude)
				ram += int(Q_(container.resources.requests['memory']).to('Mi').magnitude)
		dict = {
			'deployment_name': deploy.metadata.name,
			'service_name': deploy.spec.template.metadata.labels['service'],
			'serviceComponent_name': deploy.spec.template.metadata.labels['app.kubernetes.io/servicecomponent'],
			'cpu': cpu,
			'ram': ram
		}
		list.append(dict)
	return list

def getDeployment(ser,comp,deployments):
	for deploy in deployments:
		if (deploy['service_name'] == ser.name and deploy['serviceComponent_name'] == comp.name):
			return deploy
	return None

def getReplicas(deploy,comp):
	curr = datetime.now().replace(second=0, microsecond=0)
	fut = hist = curr + timedelta(minutes=15)
	query = data.select().where((data.servicecomponent_id == comp.id) & (data.timestamp > curr) & (data.timestamp <= fut))
	if query: 
		cpu,ram = query[0].cpu,query[0].ram
	else: 
		cpu,ram = 0,0
	requests_cpu = int(deploy['cpu'])
	requests_ram = int(deploy['ram'])
	avg = 0.75
	if requests_cpu == 0 and requests_ram == 0:
		return 1,1
	else:
		min_replicas_cpu = int(cpu/(requests_cpu+1)/avg)+1
		min_replicas_ram = int(ram/(requests_ram+1)/avg)+1
		min_replicas = min(10,max(min_replicas_cpu,min_replicas_ram))
		max_replicas = min_replicas+3
		return min_replicas,max_replicas

def body_horizontalpodautoscaler(service, component, min_replicas, max_replicas):
    target = client.V2MetricTarget(
        type='Utilization',
        average_utilization=75
    )
    
    metrics = [
        client.V2MetricSpec(
            type='Resource',
            resource=client.V2ResourceMetricSource(name='cpu', target=target)
        ),
        client.V2MetricSpec(
            type='Resource',
            resource=client.V2ResourceMetricSource(name='memory', target=target)
        )
    ]
    
    scale_target_ref = client.V2CrossVersionObjectReference(
        api_version='apps/v1',
        kind='Deployment',
        name=f"{service}-{component}"
    )
    
    spec = client.V2HorizontalPodAutoscalerSpec(
        scale_target_ref=scale_target_ref,
        min_replicas=min_replicas,
        max_replicas=max_replicas,
        metrics=metrics
    )
    
    return client.V2HorizontalPodAutoscaler(
        api_version='autoscaling/v2',
        kind='HorizontalPodAutoscaler',
        metadata=client.V1ObjectMeta(
            name=f"{service}-{component}-hpa",
            labels={'service': service, 'app.kubernetes.io/servicecomponent': component}
        ),
        spec=spec
    )

def list_horizontalpodautoscaler():
    config.load_incluster_config()
    v2 = client.AutoscalingV2Api()
    return [hpa.spec.scale_target_ref.name for hpa in v2.list_namespaced_horizontal_pod_autoscaler(namespace='default').items]

def create_or_replace_horizontalpodautoscaler(service, component, min_replicas, max_replicas, hpa_list):
    if min_replicas == 1 and max_replicas == 1:
        return 0
    
    config.load_incluster_config()
    v2 = client.AutoscalingV2Api()
    body = body_horizontalpodautoscaler(service, component, min_replicas, max_replicas)
    name = f"{service}-{component}"
    
    if name not in hpa_list:
        return v2.create_namespaced_horizontal_pod_autoscaler(namespace='default', body=body, pretty=True)
    else:
        return v2.patch_namespaced_horizontal_pod_autoscaler(name=name+'-hpa', namespace='default', body=body, pretty=True)

def delete_horizontalpodautoscaler(service, component, hpa_list):
    name = f"{service}-{component}-hpa"
    if name not in hpa_list:
        return 0
    
    config.load_incluster_config()
    v2 = client.AutoscalingV2Api()
    return v2.delete_namespaced_horizontal_pod_autoscaler(name=name, namespace='default', pretty=True)