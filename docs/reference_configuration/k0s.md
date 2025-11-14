# K0s Setup Guide

K0s is a zero-friction Kubernetes distribution that works on any Linux without additional dependencies.

## Prerequisites

See [Prerequisites](prerequesites.md) for detailed requirements.

## Single-Node Setup (Controller + Worker)

### Step 1: Install K0s

```bash
# Download and install k0s (v1.34.1)
curl -sSf https://get.k0s.sh | sudo sh

# Verify installation
k0s version
```

### Step 2: Initialize Controller with Worker

```bash
# Install controller with worker capabilities and no taints
sudo k0s install controller --enable-worker --no-taints

# Start k0s service
sudo k0s start

# Check status
sudo k0s status
```

### Step 3: Set up kubectl Access

```bash
# Create kubeconfig for kubectl
mkdir -p ~/.kube
sudo k0s kubeconfig admin > ~/.kube/config
chmod 600 ~/.kube/config

# Test kubectl access
kubectl get nodes
```

## Multi-Node Setup

### Controller Node Setup

```bash
# Install k0s
curl -sSf https://get.k0s.sh | sudo sh

# Install as controller only
sudo k0s install controller

# Start service
sudo k0s start

# Generate worker token
sudo k0s token create --role=worker > worker-token.txt

# Copy token to worker nodes (use scp, ssh, or manual copy)
```

### Worker Node Setup

```bash
# On each worker node, install k0s
curl -sSf https://get.k0s.sh | sudo sh

# Copy the token file from controller to worker
# Then install worker with token
sudo k0s install worker --token-file /path/to/worker-token.txt

# Start worker service
sudo k0s start

# Verify worker is running
sudo k0s status
```

### Verify Multi-Node Cluster

```bash
# From controller node, check all nodes
kubectl get nodes

# Check node details
kubectl get nodes -o wide
```

## Configure MetalLB Load Balancer

### Step 1: Prepare kube-proxy for MetalLB

```bash
# Edit kube-proxy configuration
kubectl edit configmap -n kube-system kube-proxy
```

Update the configuration to enable strict ARP:

```yaml
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: "iptables"
ipvs:
    strictARP: true
```

Or update K0s cluster configuration:

```bash
# Create cluster config
cat << EOF > k0s-config.yaml
apiVersion: k0s.k0sproject.io/v1beta1
kind: ClusterConfig
metadata:
  name: k0s
spec:
  network:
    kubeProxy:
      mode: iptables
      ipvs:
        strictARP: true
EOF

# Apply configuration (requires cluster restart)
sudo k0s stop
sudo k0s start --config=/path/to/k0s-config.yaml
```

### Step 2: Install MetalLB

```bash
# Install MetalLB
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.9/config/manifests/metallb-native.yaml

# Wait for MetalLB pods to be ready
kubectl wait --namespace metallb-system \
  --for=condition=ready pod \
  --selector=app=metallb \
  --timeout=90s
```

### Step 3: Configure IP Pool

```bash
# Create MetalLB configuration file
cat << EOF > metallb-ip-pool.yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: k0s-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.1.240-192.168.1.250  # Adjust to your network range
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: k0s-l2
  namespace: metallb-system
spec:
  ipAddressPools:
  - k0s-pool
EOF

# Apply MetalLB configuration
kubectl apply -f metallb-ip-pool.yaml
```

### Step 4: Verify MetalLB Setup

```bash
# Check MetalLB components
kubectl get pods -n metallb-system

# Check IP pool configuration
kubectl get ipaddresspools -n metallb-system
kubectl get l2advertisements -n metallb-system
```

## Testing the Installation

### Deploy Test Application

```bash
# Deploy the cluster-tester application
kubectl apply -f kubernetes/deploy.yaml

# Check deployment status
kubectl get deployments
kubectl get services
kubectl get pods

# Get external IP assigned by MetalLB
kubectl get svc server-benchmark-service
```

### Access Application

```bash
# Get service external IP
EXTERNAL_IP=$(kubectl get svc server-benchmark-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test endpoints
curl http://\$EXTERNAL_IP/
curl http://\$EXTERNAL_IP/fibonacci/10
curl "http://\$EXTERNAL_IP/bubble-sort?n=1024"
```

## Advanced Configuration

### Custom K0s Configuration

```bash
# Create advanced k0s configuration
cat << EOF > k0s-advanced-config.yaml
apiVersion: k0s.k0sproject.io/v1beta1
kind: ClusterConfig
metadata:
  name: k0s-cluster
spec:
  api:
    address: 192.168.1.100  # Controller IP
    port: 6443
  storage:
    type: etcd
  network:
    serviceCIDR: "10.96.0.0/12"
    podCIDR: "10.244.0.0/16"
    kubeProxy:
      mode: iptables
      ipvs:
        strictARP: true
  extensions:
    helm:
      repositories:
      - name: metallb
        url: https://metallb.github.io/metallb
      charts:
      - name: metallb
        chartname: metallb/metallb
        version: "0.14.9"
        namespace: metallb-system
EOF

# Start with custom configuration
sudo k0s install controller --config /path/to/k0s-advanced-config.yaml
```

### High Availability Setup

```bash
# For HA setup, install multiple controllers
# Controller 1
sudo k0s install controller --enable-worker

# Controller 2 & 3 (join existing cluster)
sudo k0s install controller --token-file /path/to/controller-token.txt
```

## Troubleshooting

### Common Issues

**K0s service not starting:**

```bash
# Check service status
sudo systemctl status k0scontroller
sudo systemctl status k0sworker

# Check logs
sudo journalctl -u k0scontroller -f
sudo journalctl -u k0sworker -f

# Restart services
sudo k0s stop
sudo k0s start
```

**Worker node not joining:**

```bash
# Verify token validity
sudo k0s token create --role=worker

# Check network connectivity
ping <controller-ip>
telnet <controller-ip> 6443

# Check firewall settings
sudo ufw allow 6443
sudo ufw allow 10250
```

**MetalLB not working:**

```bash
# Check kube-proxy mode
kubectl get configmap -n kube-system kube-proxy -o yaml | grep mode

# Verify IP pool configuration
kubectl describe ipaddresspool -n metallb-system

# Check MetalLB logs
kubectl logs -n metallb-system -l component=speaker
kubectl logs -n metallb-system -l component=controller
```

## Management Commands

```bash
# Stop k0s
sudo k0s stop

# Reset node (removes all data)
sudo k0s reset

# Backup cluster
sudo k0s backup --save-path /backup/

# Get cluster status
sudo k0s status

# Generate new tokens
sudo k0s token create --role=worker
sudo k0s token create --role=controller
```

## Uninstall

```bash
# Stop k0s
sudo k0s stop

# Reset and remove
sudo k0s reset
sudo rm -f /usr/local/bin/k0s

# Remove service files
sudo rm -f /etc/systemd/system/k0s*
sudo systemctl daemon-reload
```

## Next Steps

-   [Deploy the benchmark application](../../README.md#deploy-test-application)
-   [Configure cluster monitoring](../../README.md#configuration)
-   [Run your first benchmark](../../README.md#run-your-first-benchmark)
-   [Compare with other Kubernetes distributions](../../EXAMPLES.md#kubernetes-testing)
