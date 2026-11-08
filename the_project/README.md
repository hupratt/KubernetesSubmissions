# DBaaS vs. Self-Hosted Database on Kubernetes

Summary:

| Criterion | DBaaS | Self-hosted in K8s |
|---|---|---|
| **Initial effort** | Low | Medium to high (because of backups, testing and failover) |
| **Running cost (infra)** | Higher, with a premium for HA, storage and egress | Lower, since you only pay for compute and storage you already have |
| **Running cost (people)** | Low | Medium to high, and mostly invisible until something breaks |
| **Control / tuning** | Limited (extensions, parameters, versions) | Full |
| **Portability / lock-in** | Medium to high | Low |
| **Failure modes** | Your own mistakes, Provider outages, limits and bills | Your own mistakes |

---

## 1. Initial setup

### DBaaS

**Pros**
- Production-grade setup in under an hour.
- HA, automated backups, monitoring and TLS are on by default.
- Little database-specific knowledge is needed to start.

**Cons**
- The network path to the cluster must be solved (latency, private link, or traffic over the public internet).
- Provider-specific tooling (Terraform providers, IAM, parameter groups) has its own learning curve.
- Some extensions, superuser rights and config parameters are restricted.

### Self-hosted on K8s

**Pros**
- Declarative and GitOps-friendly: the database is just another manifest.
- Full control over versions, extensions, parameters and topology.
- Identical setup across dev, staging, prod and on-prem.

**Cons**
- Considerably more up-front work, including learning the operator's CRDs and failure behavior.
- Storage performance and durability depend entirely on your CSI/storage choice. Replicated block storage such as Longhorn or Ceph can add noticeable fsync latency for write-heavy workloads.
- It is easy to ship something that looks fine but has never been proven to restore.

---

## 2. Costs

### DBaaS

**Pros**
- Predictable, easy to attribute per project or client.
- No staff time spent on DB infrastructure.

**Cons**
- You pay a premium for the convenience, and it scales linearly (or worse) with size.
- Costs can spike with IOPS or egress, and many small databases get expensive quickly.

### Self-hosted on K8s

- **Infra cost:** the marginal cost of CPU, RAM and disk on nodes you already run, plus object storage for backups (cheap, often a few €/TB/month).
- **Hidden cost:** engineer time for setup, upgrades, on-call and incident handling. For a business client this is usually the dominant cost.

**Pros**
- Far cheaper per database at small to medium scale, especially when you run many databases on shared nodes.
- Cost grows with hardware, not with a vendor's price list.

**Cons**
- Capacity headroom for HA (you effectively pay for replicas and spare resources).
- A single bad incident (data loss, long outage) can wipe out years of savings.

---

## 3. Maintenance and operations

### DBaaS

**Pros**
- Minor-version patching, OS and security updates are handled by the provider.
- Automated failover, storage auto-scaling and built-in monitoring.
- Major-version upgrades are usually a guided process, and there is a support contract to call.

**Cons**
- Maintenance windows follow the provider's schedule, and forced upgrades or end-of-life deadlines happen.
- Limited visibility: no OS access, restricted logs and metrics, and diagnosing odd performance problems can be slow.
- Limited tuning (e.g. `shared_buffers`, extensions, custom builds).
- Support quality and response times vary by tier.

### Self-hosted on K8s

**Pros**
- Operators automate a lot: failover, replica creation, rolling minor updates, config reloads and some backup scheduling.
- Full access to logs, metrics, `pg_stat_*`, extensions and custom images.
- Upgrade timing is your decision.

**Cons**
- You own everything: Kubernetes upgrades (node drains must respect PDBs and replication state), operator upgrades, CRD changes, major DB version upgrades (`pg_upgrade` or logical replication, which is more manual) and security patching of images.
- Storage failures and node loss are your problem: stuck PVs, volume attach/detach delays, zone/node affinity issues with local volumes.
- Requires real database expertise (vacuum, bloat, replication lag, WAL management), not only Kubernetes expertise.
- On-call responsibility for a stateful workload on a platform designed around stateless ones.


## 4. Recommendation by scenario

- **Business-critical production for a client, small team, no dedicated DB expertise:** DBaaS. The premium buys PITR, failover and a support contract, which is cheap compared to one data-loss incident.
- **Homelab, internal tools, dev/test/staging, or many small databases:** self-hosted with an operator. It is cheaper, flexible and a good way to learn.
- **Cost-sensitive production with Kubernetes and database expertise in-house:** self-hosted is viable if you commit to:
  - a mature operator (e.g. CloudNativePG),
  - fast, reliable storage (preferably local NVMe with replication handled at the DB layer, rather than replicated block storage under a replicated DB),
  - off-cluster object-storage backups with PITR,
  - monitoring and alerting for backup and WAL failures,
  - **scheduled restore drills**.
- **Hybrid:** DBaaS for critical production data and self-hosted for everything else. Whichever you pick, take periodic logical dumps to independent storage to keep an exit path open.
