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

publish the release:

```bash
gh release create 1.3 --target=main --notes "1.3. Declarative approach is complete"
```

build the app

```bash
docker build -t hupratt/log_output:2.1 .
docker push hupratt/log_output:2.1
```

```bash
gh release create 2.3 --target=main --notes "2.3. The project is complete"
gh release create 2.4 --target=main --notes "2.4. The project is complete"
```



build the app

```bash
docker build -t hupratt/log_output:2.5 .
docker push hupratt/log_output:2.5
gh release create 2.5 --target=main --notes "2.5. The project is complete"

```

set up a test database locally

```bash
docker run -d --name pingpong-db \
  -e POSTGRES_USER=pingpong \
  -e POSTGRES_PASSWORD=pingpong \
  -e POSTGRES_DB=pingpong \
  -p 5432:5432 \
  -v pingpong-pgdata:/var/lib/postgresql/data \
  postgres:16-alpine

docker build -t hupratt/log_output:2.7 .
docker push hupratt/log_output:2.7

kubectl create secret generic postgres-auth \
  --namespace postgres \
  --from-literal=POSTGRES_USER=pingpong \
  --from-literal=POSTGRES_PASSWORD='pingpong'

gh release create 2.7 --target=main --notes "2.7. The project is complete"
docker stop pingpong-db && docker rm pingpong-db 

```