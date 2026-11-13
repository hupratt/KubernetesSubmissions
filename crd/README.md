# build and push the controller image
docker build -t hupratt/dummysite-controller:1.0 controller/
docker push hupratt/dummysite-controller:1.0

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
kubectl port-forward svc/example-site 8080:80
curl localhost:8080          # should show the "Example Domain" page