release := test

registry-core := registry.gitlab.aeros-project.eu
ifeq ($(release), test)
	registry-repo := wp3/t3.5
	tag := latest
else
	registry-repo := "aeros-public/common-deployments"
	tag := latest
endif

dockers: docker-api docker-im docker-prc docker-tm

docker-api:
	docker build docker/api --tag "$(registry-core)/$(registry-repo)/self-scaling/api:$(tag)"
docker-im:
	docker build docker/im --tag "$(registry-core)/$(registry-repo)/self-scaling/im:$(tag)"
docker-prc:
	docker build docker/prc --tag "$(registry-core)/$(registry-repo)/self-scaling/prc:$(tag)"
docker-tm:
	docker build docker/tm --tag "$(registry-core)/$(registry-repo)/self-scaling/tm:$(tag)"

kube-metrics:
	kubectl apply -f prerequisites/crds/metrics-server.yaml

install-helm: clean-helm
	helm install self-scaling helm/self-scaling/ --debug --replace

push-dockers: dockers
	docker push $(registry-core)/$(registry-repo)/self-scaling/api:latest
	docker push $(registry-core)/$(registry-repo)/self-scaling/im:latest
	docker push $(registry-core)/$(registry-repo)/self-scaling/prc:latest
	docker push $(registry-core)/$(registry-repo)/self-scaling/tm:latest

build: dockers
setup: kube-metrics push-dockers
install:  install-helm

all: build setup install

test-env: clean-helm install
	kubectl wait --for=condition=ready pods/"$$(kubectl get pods --namespace default -l\
	 "app.kubernetes.io/service=self-scaling,app.kubernetes.io/servicecomponent=api" -o jsonpath="{.items[0].metadata.name}")" --timeout=3m
	helm install test helm/test-harness/ --debug --replace
	kubectl wait --for=condition=ready pods/"$$(kubectl get pods --namespace default -l\
	 "app.kubernetes.io/instance=test,app.kubernetes.io/name=test-harness" -o jsonpath="{.items[0].metadata.name}")"
	curl -X POST "$$(kubectl get services self-scaling-api --output jsonpath='{.spec.clusterIP}')":8080/v1/services\
	 --data '{"services": [{"name": "test","managed": true,"components": [{"name": "api","managed": true}]}]}'\
	 -H 'Content-Type: application/json'

clean-helm:	
	-helm uninstall self-scaling
	-helm uninstall test
	-docker system prune --all --force

clean-sql:
	kubectl delete pvc/claim-self-scaling-db-0

sql:
	mysql -h "$$(kubectl get services self-scaling-db --output jsonpath='{.spec.clusterIP}')" --user=hpa-user --password=hpa-password