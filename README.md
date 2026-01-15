# aeriOS Self-Scaling

## Introduction
------------
This service will be able to horizontally scale (up or down) the resources devoted to a specific service (inside a node) in a dynamic fashion, based on time series inference and custom logic.

## Features
--------
aeriOS Self-Scaling service shall store time series with the usage metrics of the serviceComponent of each active service in the host cluster. Deep learning techniques based on time series models are used to predict usage metrics and horizontally scale the resources dedicated to each service component. The software will be self-contained and will act accordingly to the dynamic behaviour of each service.

Place in architecture
---------------------

![self-scaling-architecture](./images/self-scaling-architecture.png)

When the administrator user enables the aeriOS Self-Scaling controller service it automatically starts working. It accesses the metrics and stores them in its internal database, performs the deep learning process and infers to create the horizontal objects pod autoscalers dynamically. All this with pre-set values in the initial configuration.

- **API REST**: Contains the logic necessary to make GET and POST calls to intervene with the system behaviour, change default values or collect information.
- **Pod Self-Scalings Controller**: Performs the collection of metrics and is responsible for storing the values in 15-minute intervals.
- **Database storage**: Contains the history and predicted data of all serviceComponents of each active service. Also, contains the relative information about if each service are activated to infer or not.
- **Training module**: Collects the raw data from the history databases and converts it to the format needed for the deep learning process. Executes the data predictions and stores them in a new database.
- **Inference module**: Adds logic to the data in the future database and generates the inference process. Creates or replaces the horizontal pod autoscaler objects. Changes the previous values to the new ones based on the results obtained.

User guide
----------
The service has a management API that provides a flask-based REST interface that can be interacted with to configure certain values. The url must include not only the address of the service, but also the action to be performed and the message body if necessary. The response shall include the requested information or the result of the execution of a command.

| **Method** |   **Endpoint**   |             **Description**            | **Payload (if need)**                                                                                             | **Response format**                                                                                                                       |
|:----------:|:----------------:|:--------------------------------------:|-------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| GET        |   /v1/services   |     Return services and serviceComponents     |                                                                                                                   | {“services”: [{“name”: “self-scaling”,”managed”: true,”serviceComponents”: [{“name”: “api”,”managed”: true}]}]}                         |
| POST       |   /v1/services   | Update managed services and serviceComponents | {“services”: [{“name”: “self-scaling”,”managed”: true,”serviceComponents”: [{“name”: “api”,”managed”: true}]}]} | [“services managed updates sucessfully”,”Content-Type not supported!”,”Invalid JSON”,”Managed services/serviceComponents must be true or false”] |
| GET        | /v1/train-values |           Return train values          |                                                                                                                   | {“Future_data”: “1”, “History_data”: “5”}                                                                                                 |
| POST       | /v1/train-values |           Update train values          |                                     {“Future_data”: “1”, “History_data”: “5”}                                     | [“Train values changed”,”Content-Type not supported!”,”Error in json body”,”Values must be positive numbers”]                             |
| GET        |     /v1/train    | Execute the train                      |                                                                                                                   | [“Train module executed successfully”,”Not serviceComponents to train”,”Insufficient data”]                                                      |
| GET        | /v1/inference    |          Execute the inference         |                                                                                                                   | [“Infence complete sucessfully”,”Error in execution Inference Module”]                                                                    |
| GET        | /version      | Return version                            |                                                                                                                   | {“service”: “self-scaling”,”version”: “1.0.0”}                                                                                   |
| GET        |    /v1/health    | Return health status                   |                                                                                                                   | {“status”: “healthy”}                                                                                                                     |
| GET        |  /v1/api-export  | Return OpenAPI JSON format             |                                                                                                                   | {“openapi”: “3.0.0”,”info”: {…}}                                                                                                          |

Prerequisites
-------------
1. **Kubernetes and Helm environment**. The kubernetes and helm configuration must be applied.

```python
sudo self-scaling/deployment/prerequisites/scripts/kubernetes.sh -t SERVER -p 10.210.0.0/16 
```

2. **Kubernetes metrics**. In order for the service to work properly, the metrics must be enabled in the kubernetes configuration.

```python
kubectl apply -f self-scaling/deployment/prerequisites/crds/metrics-server.yaml
```

Installation minimum requirements
-------------
- **Operating Systems supported**
    - Linux (Ubuntu18.04/20.04)
    - Debian (9/10/11)
- **CPU**: 
    - **2 cores** is the **recommended** minimum number of cores.
    - **4 cores** is the **optimal** number of cores.
- **Memory**:
    - **3 GB RAM** is the **required** minimum memory size. 
- **Storage**:
    - **1 GB** is the **required** minimum storage size.

Installation
------------
service is provided as a Helm chart. Refer to specific deployment instructions.

```sh
git clone https://github.com/eclipse-aerios/self-scaling
helm install self-scaling self-scaling/deployment/helm/self-scaling/ --debug
```

Version control and release
---------------------------
Version 1.0.0. 