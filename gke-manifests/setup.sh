sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo << EOM\n[google-cloud-cli]\nname=Google Cloud CLI\nbaseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el9-x86_64\nenabled=1\ngpgcheck=1\nrepo_gpgcheck=0\ngpgkey=https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg\nEOM
sudo dnf install libxcrypt-compat.x86_64
sudo dnf install google-cloud-cli
sudo dnf install google-cloud-cli-gke-gcloud-auth-plugin
gcloud -v
gcloud auth login
gcloud config set project project-f5db746b-2bc2-4fda-a87 
gcloud config list project
gcloud container clusters create dwk-cluster --zone=europe-north1-b --cluster-version=1.37 --disk-size=32 --num-nodes=4 --machine-type=e2-standard-2 --gateway-api=standard

gh release create 3.1 --target=main --notes "3.1. The project is complete"
gh release create 3.5 --target=main --notes "3.5. The project is complete"

# setup a service account that can deploy to the GCP cluster
gcloud iam service-accounts create "github-actions-sa" --display-name="GitHub Actions SA"
gcloud projects add-iam-policy-binding project-f5db746b-2bc2-4fda-a87 \
  --role="roles/artifactregistry.writer" \
  --member="serviceAccount:github-actions-sa@project-f5db746b-2bc2-4fda-a87.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding project-f5db746b-2bc2-4fda-a87 \
  --role="roles/container.admin" \
  --member="serviceAccount:github-actions-sa@project-f5db746b-2bc2-4fda-a87.iam.gserviceaccount.com"

# so that github's SA can list NEGs
gcloud projects add-iam-policy-binding project-f5db746b-2bc2-4fda-a87 \
  --role="roles/compute.networkAdmin" \
  --member="serviceAccount:github-actions-sa@project-f5db746b-2bc2-4fda-a87.iam.gserviceaccount.com"

# so that github's SA can delete NEGs

gcloud iam roles create negDelete \
  --project=project-f5db746b-2bc2-4fda-a87 \
  --title="NEG delete" \
  --permissions=compute.networkEndpointGroups.delete

gcloud projects add-iam-policy-binding project-f5db746b-2bc2-4fda-a87 \
  --role="projects/project-f5db746b-2bc2-4fda-a87/roles/negDelete" \
  --member="serviceAccount:github-actions-sa@project-f5db746b-2bc2-4fda-a87.iam.gserviceaccount.com"

gcloud iam workload-identity-pools create "github-pool" \
  --location="global" \
  --display-name="GitHub Actions Pool"

gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='hupratt/KubernetesSubmissions'" \
  --issuer-uri="https://token.actions.githubusercontent.com"

gcloud iam service-accounts add-iam-policy-binding \
  github-actions-sa@project-f5db746b-2bc2-4fda-a87.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet

# allows the cluster to pull docker images from the registry by giving the default service account read perms
gcloud artifacts repositories add-iam-policy-binding my-docker-reg \
  --location=europe-north1 \
  --project=project-f5db746b-2bc2-4fda-a87 \
  --member="serviceAccount:602773526588-compute@developer.gserviceaccount.com" \
  --role=roles/artifactregistry.reader

gh release create 3.6 --target=main --notes "3.6. The project is complete"
gh release create 3.7 --target=main --notes "3.7. The project is complete"
gh release create 3.8 --target=main --notes "3.8. The project is complete"


# debug neg and backend

➜ ~ gcloud compute backend-services list --global --filter="alleluya"     
NAME                                             BACKENDS                                                                             PROTOCOL
gkegw1-h6d9-alleluya-todo-svc-2345-b31olt0j2l79  europe-north1-b/networkEndpointGroups/k8s1-196b4833-alleluya-todo-svc-2345-57f7401d  HTTP
➜ ~ gcloud compute network-endpoint-groups list --filter="alleluya"  
NAME                                           LOCATION         ENDPOINT_TYPE   SIZE
k8s1-196b4833-alleluya-todo-svc-2345-57f7401d  europe-north1-b  GCE_VM_IP_PORT  1


gh release create 3.9 --target=main --notes "3.9. The project is complete"


# pg_dump SA via cronjob

gcloud iam service-accounts create "my-storage-sa" --display-name="Pod Storage SA"

gcloud projects add-iam-policy-binding project-f5db746b-2bc2-4fda-a87 \
  --role="roles/storage.objectCreator" \
  --member="serviceAccount:my-storage-sa@project-f5db746b-2bc2-4fda-a87.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding project-f5db746b-2bc2-4fda-a87 \
  --role="roles/storage.objectViewer" \
  --member="serviceAccount:my-storage-sa@project-f5db746b-2bc2-4fda-a87.iam.gserviceaccount.com"

# lets you grant yourself policyAdmin on the org
gcloud organizations add-iam-policy-binding 19073322258 \
  --member="user:rboui534@gmail.com" \
  --role="roles/orgpolicy.policyAdmin"

# disable enforcement for just this project
cat > policy.yaml <<'EOF'
name: projects/project-f5db746b-2bc2-4fda-a87/policies/iam.disableServiceAccountKeyCreation
spec:
  rules:
  - enforce: false
EOF

gcloud org-policies set-policy policy.yaml

# create the key
gcloud iam service-accounts keys create key.json \
  --iam-account=my-storage-sa@project-f5db746b-2bc2-4fda-a87.iam.gserviceaccount.com

# import into k8s
kubectl create secret -n project generic storage-sa-key --from-file=key.json=key.json

# apply rentention policy
gcloud storage buckets update gs://todo_bucket_1 --lifecycle-file=retention.json

gh release create 3.10 --target=main --notes "3.10. The project is complete"

gh release create 3.11 --target=main --notes "3.11. The project is complete"
gh release create 3.12 --target=main --notes "3.12. The project is complete"
gh release create 4.1 --target=main --notes "4.1. The project is complete"
gh release create 4.2 --target=main --notes "4.2. The project is complete"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm upgrade --install prom prometheus-community/prometheus \
  --namespace monitoring \
  --create-namespace \
  --values prom-values.yaml

helm upgrade --install loki grafana/loki \
  --namespace monitoring \
  --values loki-values.yaml

helm upgrade --install k8smon grafana/k8s-monitoring \
  --namespace monitoring \
  --values k8smon-values.yaml

helm upgrade --install grafana grafana/grafana \
  --namespace monitoring \
  --values grafana-values.yaml

gh release create 4.3 --target=main --notes "4.3. The project is complete"

kubectl create namespace argo-rollouts
# this will error out because of some *** annotation
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
# this one won't
kubectl apply --server-side --force-conflicts -n argo-rollouts \
  -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml


kubectl get pods -l app=flaky-update -o 'custom-columns=NAME:.metadata.name,IMAGES:.spec.containers[*].image' -w

# or download the plugin
curl -LO https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-amd64
chmod +x kubectl-argo-rollouts-linux-amd64
sudo mv kubectl-argo-rollouts-linux-amd64 /usr/local/bin/kubectl-argo-rollouts

# and run it
kubectl argo rollouts get rollout flaky-update-dep -w

# and rollback to working replicaset
kubectl argo rollouts undo flaky-update-dep --to-revision=4


kubectl argo rollouts get rollout logoutput -n exercises -w
gh release create 4.4 --target=main --notes "4.4. The project is complete"

# and check out the analysis' report:

kubectl get analysisruns -n exercises    
NAME                       STATUS       AGE
logoutput-5dfc4bb6fc-3-1   Successful   9m50s
logoutput-84844b4bfc-2-1   Successful   13m
logoutput-85fd88ddb9-4-1   Error        8m2s
kubectl describe analysisruns logoutput-85fd88ddb9-4-1 -n exercises

gh release create 4.5 --target=main --notes "4.5. The project is complete"

gcloud container node-pools update default-pool \
  --cluster=dwk-cluster \
  --location=europe-north1-b \
  --machine-type=e2-medium


helm repo add nats https://nats-io.github.io/k8s/helm/charts/
helm repo update
helm upgrade --install my-nats nats/nats \
  --namespace nats \
  --create-namespace \
  --set promExporter.enabled=true

gh release create 4.6 --target=main --notes "4.6. The project is complete"

kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

kubectl patch configmap argocd-cmd-params-cm -n argocd \
  --type merge -p '{"data":{"server.insecure":"true"}}'
kubectl rollout restart deployment argocd-server -n argocd

kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d; echo

gh release create 4.7 --target=main --notes "4.7. The project is complete"
gh release create 4.8 --target=main --notes "4.8. The project is complete"

git commit --allow-empty -m "Kickstart staging queue" && git push

git add -A
git commit -m "just a message"
git tag -a v1.5 -m "Release v1.5"
git push origin main
git push origin refs/tags/v1.5

export DATABASE_URL="postgresql://postgres:strongpw@localhost:5432/todos"
export NATS_ENABLED=False
export DISCORD_ENABLED=False
uv run fastapi run src/todo_app/main.py --host 0.0.0.0 --port 8000

gh release create 4.9 --target=main --notes "4.9. The project is complete"
gh release create 4.10 --target=main --notes "4.10. The project is complete"

gh release create 5.1 --target=main --notes "5.1. The project is complete"

curl -L https://istio.io/downloadIstio | sh -
cd istio-1.32.0/bin
./istioctl version
./istioctl install --set profile=ambient --skip-confirmation
kubectl get crd gateways.gateway.networking.k8s.io &> /dev/null || \
  kubectl apply --server-side -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.6.1/experimental-install.yaml

k apply -f https://raw.githubusercontent.com/istio/istio/release-1.32/samples/bookinfo/platform/kube/bookinfo.yaml
k apply -f https://raw.githubusercontent.com/istio/istio/release-1.32/samples/bookinfo/platform/kube/bookinfo-versions.yaml
k apply -f https://raw.githubusercontent.com/istio/istio/release-1.32/samples/bookinfo/gateway-api/bookinfo-gateway.yaml

kubectl label namespace default istio.io/dataplane-mode=ambient

k apply -f kiali.yaml

./istioctl dashboard kiali
for i in $(seq 1 100); do curl -sSI -o /dev/null http://34.88.205.168/productpage; done

k apply -f https://raw.githubusercontent.com/istio/istio/release-1.32/samples/curl/curl.yaml    
kubectl exec deploy/curl -- curl -s "http://productpage:9080/productpage"

kubectl apply -f - <<EOF
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: productpage-ztunnel
  namespace: default
spec:
  selector:
    matchLabels:
      app: productpage
  action: ALLOW
  rules:
  - from:
    - source:
        principals:
        - cluster.local/ns/default/sa/bookinfo-gateway-istio
EOF

kubectl exec deploy/curl -- curl -s "http://productpage:9080/productpage"


gh release create 5.2 --target=main --notes "5.2. The project is complete"
