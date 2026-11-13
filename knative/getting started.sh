➜ ~ k apply -f hello-world.yaml
➜ ~ k apply -f hello-knative.yaml

➜ ~ curl "$(kn service describe hello -o url)"
Hello World!
➜ ~ curl $(kubectl get ksvc hello -o jsonpath='{.status.url}')
Hello World!
➜ ~ sudo dnf install -y golang
➜ ~ go install github.com/rakyll/hey@v0.1.5
➜ ~ sudo mv ~/go/bin/hey /usr/local/bin/hey
➜ ~ hey -z 30s -c 100 $(kubectl get ksvc hello -o jsonpath='{.status.url}')

Summary:
  Total:        30.0248 secs
  Slowest:      0.3860 secs
  Fastest:      0.0037 secs
  Average:      0.0365 secs
  Requests/sec: 2735.0745
  
  Total data:   1067560 bytes
  Size/request: 13 bytes

Response time histogram:
  0.004 [1]     |
  0.042 [67056] |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
  0.080 [14723] |■■■■■■■■■
  0.118 [229]   |
  0.157 [11]    |
  0.195 [0]     |
  0.233 [0]     |
  0.271 [0]     |
  0.310 [4]     |
  0.348 [9]     |
  0.386 [87]    |


Latency distribution:
  10%% in 0.0201 secs
  25%% in 0.0219 secs
  50%% in 0.0400 secs
  75%% in 0.0413 secs
  90%% in 0.0435 secs
  95%% in 0.0536 secs
  99%% in 0.0693 secs

Details (average, fastest, slowest):
  DNS+dialup:   0.0003 secs, 0.0000 secs, 0.2711 secs
  DNS-lookup:   0.0003 secs, 0.0000 secs, 0.2704 secs
  req write:    0.0000 secs, 0.0000 secs, 0.0055 secs
  resp wait:    0.0361 secs, 0.0035 secs, 0.1352 secs
  resp read:    0.0000 secs, 0.0000 secs, 0.0020 secs

Status code distribution:
  [200] 82120 responses