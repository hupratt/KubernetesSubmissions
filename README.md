# KubernetesSubmissions

#### Circle the logo of every product / project you've used


1) grafana: i have installed grafana using the "kube-prometheus-stack" helm chart and configured the integrations with for example SNMP providers (synology), prometheus exporters and OTEL to collect metrics, logs and traces from a .NET application 
2) authentik: i have implemented identity and access management with oidc and SSH single sign-on with authentik which allows me to schedule LDAP syncs and have Active Directory integration
3) kyverno: i use kyverno as an admission controller — no privileged/root containers, required resource limits, no latest tags, blocked dangerous capabilities. Deployed via the official helm chart
4) cloud native postgres: i have 2 CNPG clusters in my home-prod. One for immich and the another shared cluster for Authentik, NetBox, PostHog, Django apps, Grafana, Harbor, linkwarden, paperless-ngx and patchmon. Deployed via the official chart with the operator. I'm using the ghcr.io/cloudnative-pg/cloudnative-pg operator and the cloudnative-pg chart to deploy clusters that run postgis and cloudnative-vectorchord

## Exercises

### Chapter 2

- [1.1.](https://github.com/hupratt/KubernetesSubmissions/tree/1.1/)
- [1.2.](https://github.com/hupratt/KubernetesSubmissions/tree/1.2/)
- [1.3.](https://github.com/hupratt/KubernetesSubmissions/tree/1.3/)
- [1.4.](https://github.com/hupratt/KubernetesSubmissions/tree/1.4/)
- [1.5.](https://github.com/hupratt/KubernetesSubmissions/tree/1.5/)
- [1.6.](https://github.com/hupratt/KubernetesSubmissions/tree/1.6/)
- [1.7.](https://github.com/hupratt/KubernetesSubmissions/tree/1.7/)
- [1.8.](https://github.com/hupratt/KubernetesSubmissions/tree/1.8/)
- [1.9.](https://github.com/hupratt/KubernetesSubmissions/tree/1.9/)
- [1.10.](https://github.com/hupratt/KubernetesSubmissions/tree/1.10/)
- [1.11.](https://github.com/hupratt/KubernetesSubmissions/tree/1.11/)
- [1.12.](https://github.com/hupratt/KubernetesSubmissions/tree/1.12/)
- [1.13.](https://github.com/hupratt/KubernetesSubmissions/tree/1.13/)

### Chapter 3

- [2.1.](https://github.com/hupratt/KubernetesSubmissions/tree/2.1/)
- [2.2.](https://github.com/hupratt/KubernetesSubmissions/tree/2.2/)
- [2.3.](https://github.com/hupratt/KubernetesSubmissions/tree/2.3/)
- [2.4.](https://github.com/hupratt/KubernetesSubmissions/tree/2.4/)
- [2.5.](https://github.com/hupratt/KubernetesSubmissions/tree/2.5/)
- [2.6.](https://github.com/hupratt/KubernetesSubmissions/tree/2.6/)
- [2.7.](https://github.com/hupratt/KubernetesSubmissions/tree/2.7/)
- [2.8.](https://github.com/hupratt/KubernetesSubmissions/tree/2.8/)
- [2.9.](https://github.com/hupratt/KubernetesSubmissions/tree/2.9/)
- [2.10.](https://github.com/hupratt/KubernetesSubmissions/tree/2.10/)

### Chapter 4

- [3.1.](https://github.com/hupratt/KubernetesSubmissions/tree/3.1/)
- [3.2.](https://github.com/hupratt/KubernetesSubmissions/tree/3.2/)
- [3.3.](https://github.com/hupratt/KubernetesSubmissions/tree/3.3/)
- [3.4.](https://github.com/hupratt/KubernetesSubmissions/tree/3.4/)
- [3.5.](https://github.com/hupratt/KubernetesSubmissions/tree/3.5/)
- [3.6.](https://github.com/hupratt/KubernetesSubmissions/tree/3.6/)
- [3.7.](https://github.com/hupratt/KubernetesSubmissions/tree/3.7/)
- [3.8.](https://github.com/hupratt/KubernetesSubmissions/tree/3.8/)
- [3.9.](https://github.com/hupratt/KubernetesSubmissions/tree/3.9/)
- [3.10.](https://github.com/hupratt/KubernetesSubmissions/tree/3.10/)
- [3.11.](https://github.com/hupratt/KubernetesSubmissions/tree/3.11/)
- [3.12.](https://github.com/hupratt/KubernetesSubmissions/tree/3.12/)

### Chapter 5

- [4.1.](https://github.com/hupratt/KubernetesSubmissions/tree/4.1/)
- [4.2.](https://github.com/hupratt/KubernetesSubmissions/tree/4.2/)
- [4.3.](https://github.com/hupratt/KubernetesSubmissions/tree/4.3/)
- [4.4.](https://github.com/hupratt/KubernetesSubmissions/tree/4.4/)
- [4.5.](https://github.com/hupratt/KubernetesSubmissions/tree/4.5/)
- [4.6.](https://github.com/hupratt/KubernetesSubmissions/tree/4.6/)
- [4.7.](https://github.com/hupratt/KubernetesSubmissions/tree/4.7/)
- [4.8.](https://github.com/hupratt/KubernetesSubmissions/tree/4.8/)
- [4.9.](https://github.com/hupratt/KubernetesSubmissions/tree/4.9/)
- [4.10.](https://github.com/hupratt/KubernetesSubmissions/tree/4.10/)

### Chapter 6

- [5.1.](https://github.com/hupratt/KubernetesSubmissions/tree/5.1/)
- [5.2.](https://github.com/hupratt/KubernetesSubmissions/tree/5.2/)
- [5.3.](https://github.com/hupratt/KubernetesSubmissions/tree/5.3/)
- [5.4.](https://github.com/hupratt/KubernetesSubmissions/tree/5.4/)
- [5.5.](https://github.com/hupratt/KubernetesSubmissions/tree/5.5/)
- [5.6.](https://github.com/hupratt/KubernetesSubmissions/tree/5.6/)
- [5.7.](https://github.com/hupratt/KubernetesSubmissions/tree/5.7/)
- [5.8.](https://github.com/hupratt/KubernetesSubmissions/tree/5.8/)
- [5.9.](https://github.com/hupratt/KubernetesSubmissions/tree/5.9/)
