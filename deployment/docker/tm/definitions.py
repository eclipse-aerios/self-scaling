from mysql_conf import *
from random import randint

def getServiceComponents():
	query = (serviceComponent.select(serviceComponent.id,serviceComponent.service_id,service.name,serviceComponent.name).join(service)).dicts()
	dict = []
	for q in query:
		dict.append(q)
	return dict

def getResources(comp,curr,hist):
	dataCPU = []
	dataRAM = []
	query = data.select().where((data.servicecomponent_id==comp['id']) & (data.timestamp >= hist) & (data.timestamp < curr))
	for q in query:
		dataCPU.append([q.timestamp,q.cpu+randint(0,1)])
		dataRAM.append([q.timestamp,q.ram+randint(0,1)])
	return dataCPU,dataRAM

def setMetrics(values):
	for val in values:
		try:
			data.get(
        		(data.service_id == val['service_id']) &
        		(data.servicecomponent_id == val['servicecomponent_id']) &
				(data.timestamp == val['timestamp'])
			)
		except data.DoesNotExist:
			data.create(**val)
			continue
		data.update(**val).where(
			data.service_id==val['service_id'],
			data.servicecomponent_id==val['servicecomponent_id'],
			data.timestamp==val['timestamp'],
			data.real == val['real']
		).execute()