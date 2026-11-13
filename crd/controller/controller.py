import logging
import time

from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

# used to filter later on on dummysites
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


def build_deployment(name, ns, url, ds):
    labels = {"app": name}
    html_mount = client.V1VolumeMount(name="html", mount_path="/usr/share/nginx/html")

    init = client.V1Container(
        name="fetch",
        image="curlimages/curl:8.10.1",
        command=["sh", "-c", 'curl -fsSL "$URL" -o /html/index.html'],
        env=[client.V1EnvVar(name="URL", value=url)],
        volume_mounts=[client.V1VolumeMount(name="html", mount_path="/html")],
    )
    web = client.V1Container(
        name="nginx",
        image="nginx:1.27-alpine",
        ports=[client.V1ContainerPort(container_port=80)],
        volume_mounts=[html_mount],
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
                    containers=[web],
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
