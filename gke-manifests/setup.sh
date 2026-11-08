sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo << EOM\n[google-cloud-cli]\nname=Google Cloud CLI\nbaseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el9-x86_64\nenabled=1\ngpgcheck=1\nrepo_gpgcheck=0\ngpgkey=https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg\nEOM
sudo dnf install libxcrypt-compat.x86_64
sudo dnf install google-cloud-cli
sudo dnf install google-cloud-cli-gke-gcloud-auth-plugin
gcloud -v
gcloud auth login
gcloud config set project project-f5db746b-2bc2-4fda-a87 
gcloud config list project
gcloud container clusters create dwk-cluster --zone=europe-north1-b --cluster-version=1.37 --disk-size=32 --num-nodes=4 --machine-type=e2-medium --gateway-api=standard

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
