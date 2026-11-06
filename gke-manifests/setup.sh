sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo << EOM\n[google-cloud-cli]\nname=Google Cloud CLI\nbaseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el9-x86_64\nenabled=1\ngpgcheck=1\nrepo_gpgcheck=0\ngpgkey=https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg\nEOM
sudo dnf install libxcrypt-compat.x86_64
sudo dnf install google-cloud-cli
sudo dnf install google-cloud-cli-gke-gcloud-auth-plugin
gcloud -v
gcloud auth login
gcloud config set project project-f5db746b-2bc2-4fda-a87 
gcloud config list project
gcloud container clusters create dwk-cluster --zone=europe-north1-b --cluster-version=1.37 --disk-size=32 --num-nodes=4 --machine-type=e2-medium