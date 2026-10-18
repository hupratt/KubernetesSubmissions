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

tag is assigned to the wrong commit because it got created automatically with our earlier gh command

```bash
git fetch --tags
# delete locally and on github
git tag -d 1.1
git push origin --delete 1.1
# tag the right commit and push it to the remote
git tag 1.1 c8e99bacdf17dfb094c202d10f25903da7083950
git push origin 1.1
# list
git tag -n
```