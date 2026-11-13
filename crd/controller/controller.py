import logging
import time

from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

GROUP, VERSION, PLURAL = "stable.dwk", "v1", "dummysites"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("dummysite")


def owner_ref(ds):
    return client.V1OwnerReference(
        api_version=f"{GROUP}/{VERSION}",
        kind="DummySite",
        name=ds["metadata"]["name"],
        uid=ds["metadata"]["uid"],
        controller=True,
    )


FETCH_SCRIPT = 'curl -fsSL -A "$UA" "$URL" -o /html/index.html.tmp && mv /html/index.html.tmp /html/index.html'

# Sidecar: sleep 5-15 min, fetch a random Wikipedia page, repeat forever.
# Written to a temp file first and moved, so nginx never serves a half-written page.
RANDOM_SCRIPT = """
while true; do
  delay=$(awk 'BEGIN{srand(); print int(300 + rand() * 601)}')
  echo "sleeping ${delay}s"
  sleep "$delay"
  if curl -fsSL -A "$UA" "$RANDOM_URL" -o /html/random.html.tmp; then
    mv /html/random.html.tmp /html/random.html
    echo "saved new random page"
  else
    echo "fetch failed, will retry next round"
  fi
done
"""

USER_AGENT = "dummysite-controller/1.0 (Kubernetes learning exercise)"
RANDOM_URL = "https://en.wikipedia.org/wiki/Special:Random"


def build_deployment(name, ns, url, ds):
    labels = {"app": name}
    ua = client.V1EnvVar(name="UA", value=USER_AGENT)

    def html_mount(path):
        return client.V1VolumeMount(name="html", mount_path=path)

    # init container: runs once, saves website_url as index.html
    init = client.V1Container(
        name="fetch",
        image="curlimages/curl:8.10.1",
        command=["sh", "-c", FETCH_SCRIPT],
        env=[client.V1EnvVar(name="URL", value=url), ua],
        volume_mounts=[html_mount("/html")],
    )
    # main container: serves the shared directory
    main = client.V1Container(
        name="main",
        image="nginx:1.27-alpine",
        ports=[client.V1ContainerPort(container_port=80)],
        volume_mounts=[html_mount("/usr/share/nginx/html")],
    )
    # sidecar: keeps writing a new random page to random.html
    sidecar = client.V1Container(
        name="random-page",
        image="curlimages/curl:8.10.1",
        command=["sh", "-c", RANDOM_SCRIPT],
        env=[client.V1EnvVar(name="RANDOM_URL", value=RANDOM_URL), ua],
        volume_mounts=[html_mount("/html")],
    )
    return client.V1Deployment(
        metadata=client.V1ObjectMeta(
            name=name, namespace=ns, labels=labels, owner_references=[owner_ref(ds)]
        ),
        spec=client.V1DeploymentSpec(
            replicas=1,
            selector=client.V1LabelSelector(match_labels=labels),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels),
                spec=client.V1PodSpec(
                    init_containers=[init],
                    containers=[main, sidecar],
                    volumes=[client.V1Volume(name="html", empty_dir=client.V1EmptyDirVolumeSource())],
                ),
            ),
        ),
    )


def build_service(name, ns, ds):
    return client.V1Service(
        metadata=client.V1ObjectMeta(name=name, namespace=ns, owner_references=[owner_ref(ds)]),
        spec=client.V1ServiceSpec(
            selector={"app": name},
            ports=[client.V1ServicePort(port=80, target_port=80)],
        ),
    )


def reconcile(ds, apps, core):
    ns = ds["metadata"]["namespace"]
    name = f"{ds['metadata']['name']}-site"
    url = ds["spec"]["website_url"]

    dep = build_deployment(name, ns, url, ds)
    svc = build_service(name, ns, ds)

    try:
        apps.create_namespaced_deployment(ns, dep)
        log.info("created deployment %s/%s for %s", ns, name, url)
    except ApiException as e:
        if e.status != 409:
            raise
        apps.patch_namespaced_deployment(name, ns, dep)  # URL may have changed
        log.info("patched deployment %s/%s", ns, name)

    try:
        core.create_namespaced_service(ns, svc)
        log.info("created service %s/%s", ns, name)
    except ApiException as e:
        if e.status != 409:
            raise


def main():
    config.load_incluster_config()
    custom = client.CustomObjectsApi()
    apps = client.AppsV1Api()
    core = client.CoreV1Api()

    while True:
        try:
            w = watch.Watch()
            for event in w.stream(custom.list_cluster_custom_object, GROUP, VERSION, PLURAL):
                if event["type"] in ("ADDED", "MODIFIED"):
                    try:
                        reconcile(event["object"], apps, core)
                    except Exception:
                        log.exception("reconcile failed")
                # DELETED: nothing to do, ownerReferences make the GC remove children
        except Exception:
            log.exception("watch broke, restarting in 5s")
            time.sleep(5)


if __name__ == "__main__":
    main()
