setting up a release from the CLI

```bash
sudo dnf install gh
gh auth login
gh release create 1.1 --target=main --notes "first exercise is complete"
```

build the app

```bash
docker build -t hupratt/log_output:1.1 .
docker push hupratt/log_output --all-tags 
```

if that fails with "requested access to the resource is denied", make sure to login again

```bash
docker logout
docker login -u hupratt
```

run the image in k3d

```bash
kubectl create deployment logoutput --image=hupratt/log_output:1.1
```