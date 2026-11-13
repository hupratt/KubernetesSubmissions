➜ ~ kn revisions list
NAME          SERVICE   TRAFFIC   TAGS   GENERATION   AGE     CONDITIONS   READY   REASON
hello-00002   hello     100%             2            19s     4 OK / 4     True    
hello-00001   hello                      1            9m17s   3 OK / 4     Tru

➜ knative (main) ✗ kn service update hello \
--traffic hello-00001=50 \
--traffic @latest=50
Warning: Kubernetes default value is insecure, Knative may default this to secure in a future release: spec.template.spec.containers[0].securityContext.allowPrivilegeEscalation, spec.template.spec.containers[0].securityContext.capabilities, spec.template.spec.containers[0].securityContext.runAsNonRoot, spec.template.spec.containers[0].securityContext.seccompProfile
Updating Service 'hello' in namespace 'default':

  0.027s The Route is still working to reflect the latest desired specification.
  0.065s Ingress has not yet been reconciled.
  0.092s Waiting for load balancer to be ready
  0.281s Ready to serve.

Service 'hello' with latest revision 'hello-00002' (unchanged) is available at URL:
http://hello.default.172.21.0.2.sslip.io

➜ ~ kn revisions list
NAME          SERVICE   TRAFFIC   TAGS   GENERATION   AGE   CONDITIONS   READY   REASON
hello-00002   hello     50%              2            89s   3 OK / 4     True    
hello-00001   hello     50%              1            10m   4 OK / 4     True

➜ knative (main) ✗ echo "Accessing URL $(kn service describe hello -o url)"
curl "$(kn service describe hello -o url)"
Accessing URL http://hello.default.172.21.0.2.sslip.io
Hello Knative!
➜ knative (main) ✗ curl "$(kn service describe hello -o url)"
Hello Knative!
➜ knative (main) ✗ curl "$(kn service describe hello -o url)"
Hello World!
➜ knative (main) ✗ 