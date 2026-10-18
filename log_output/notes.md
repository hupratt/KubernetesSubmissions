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