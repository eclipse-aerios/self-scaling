#!/usr/bin/python3

from datetime import datetime, timedelta
from io import BufferedRandom
from definitions import *

def inference():

    deployments = getDeployments()
    services = getServices()
    list = list_horizontalpodautoscaler()
    for en in services:
        service = getService(en)
        if not service: continue
        components = getServiceComponents(en)
        for comp in components:
            component = getServiceComponent(service.id,comp)
            if not component: continue
            if service.infer and component.infer:
                deploy = getDeployment(service,component,deployments)
                if not deploy: continue
                min_replicas,max_replicas = getReplicas(deploy,component)
                create_or_replace_horizontalpodautoscaler(service.name,component.name,min_replicas,max_replicas,list)
            else:
                delete_horizontalpodautoscaler(service.name,component.name,list)
    return 'Inference complete sucessfully'