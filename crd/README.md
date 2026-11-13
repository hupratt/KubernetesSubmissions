# build and push the controller image
docker build -t europe-north1-docker.pkg.dev/project-f5db746b-2bc2-4fda-a87/my-docker-reg/dummysite-controller:1.0 controller/
docker push europe-north1-docker.pkg.dev/project-f5db746b-2bc2-4fda-a87/my-docker-reg/dummysite-controller:1.0

# CRD first, so the API knows the kind
kubectl apply -f manifests/crd.yaml

# 1. role, account and binding
kubectl apply -f manifests/rbac.yaml
# 2. controller deployment
kubectl apply -f manifests/controller-deployment.yaml
# 3. the DummySite
kubectl apply -f manifests/dummysite.yaml

# verify
kubectl get ds
kubectl get deploy,svc,pods
kubectl port-forward svc/random-dummysite-site 9635:80 -c main
curl localhost:9635