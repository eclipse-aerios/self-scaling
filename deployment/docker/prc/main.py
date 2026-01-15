import sys
import time
from datetime import datetime
from definitions import *

delay = 15

while True:

	serviceComponents = getServiceComponents()

	if not serviceComponents:
		time.sleep(10)
		continue

	stop = False
	cpuSUM = list(range(len(serviceComponents)))
	ramSUM = list(range(len(serviceComponents)))
	minutes = 0

	while not stop:
		metrics = getMetrics()
		for i,comp in enumerate(serviceComponents):
			cpu,ram = getResources(comp,metrics)
			cpuSUM[i] += cpu
			ramSUM[i] += ram
		start = time.time()
		time.sleep(60.0 - time.localtime(start).tm_sec)
		fin = int(time.localtime(start).tm_min+1)
		minutes += 1

		if(fin%delay==0): stop = True

	timestamp = datetime.now().replace(second=0,microsecond=0)
	d = []

	for i,comp in enumerate(serviceComponents):
		cpu = int(cpuSUM[i]/minutes)
		ram = int(ramSUM[i]/minutes)
		if not (cpu > 0 or ram > 0):
			continue
		dict = {
			'service_id' : comp['service_id'],
			'servicecomponent_id': comp['id'],
			'timestamp': timestamp,
			'cpu' : cpu,
			'ram' : ram,
			'real': 1
		}
		d.append(dict)
	print(d)
	setMetrics(d)