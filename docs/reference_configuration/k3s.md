# K3s Setup Guide

K3s is a lightweight Kubernetes distribution designed for IoT and edge computing environments.

## Prerequisites

See [Prerequisites](prerequisites.md) for detailed requirements.

## Single-Node Setup

### Step 1: Install K3s Server (Control Plane)

```bash
# Install K3s without the default ServiceLB (Klipper)
# We disable it to use MetalLB instead
curl -sfL https://get.k3s.io | sh -s - --disable=servicelb

# Wait for K3s to be ready
sudo k3s kubectl get nodes

# Check if all pods are running
sudo k3s kubectl get pods -A
```

### Step 2: Set up kubectl Access

```bash
# Create kubectl config directory
mkdir -p ~/.kube

# Copy K3s kubeconfig
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown \$USER:\$USER ~/.kube/config

# Test kubectl access
kubectl get nodes
```

## Multi-Node Setup

### Server (Control Plane) Setup

```bash
# Install K3s server without ServiceLB
curl -sfL https://get.k3s.io | sh -s - --disable=servicelb

# Get the node token for worker nodes
sudo cat /var/lib/rancher/k3s/server/node-token

# Note: Save this token for worker node setup
```

### Worker Node Setup

```bash
# Install K3s agent (worker) on each worker node
# Replace <SERVER_IP> with your server's IP address
# Replace <NODE_TOKEN> with the token from the server
curl -sfL https://get.k3s.io | K3S_URL=https://<SERVER_IP>:6443 K3S_TOKEN=<NODE_TOKEN> sh -s - --disable=servicelb
```

### Verify Multi-Node Cluster

```bash
# From server node, check all nodes
kubectl get nodes -o wide

# Check node status
kubectl describe nodes
```

## Alternative: Modify Existing Installation

If K3s is already installed with ServiceLB, you can disable it:

```bash
# Edit the K3s service configuration
sudo nano /etc/systemd/system/k3s.service

# Add --disable=servicelb to the ExecStart line
# Example:
# ExecStart=/usr/local/bin/k3s server --disable=servicelb

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart k3s

# Verify ServiceLB is disabled
kubectl get pods -n kube-system | grep svclb
# Should return no results
```

## Configure MetalLB Load Balancer

### Step 1: Install MetalLB

```bash
# Install MetalLB manifest
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.9/config/manifests/metallb-native.yaml

# Wait for MetalLB to be ready
kubectl wait --namespace metallb-system \
  --for=condition=ready pod \
  --selector=app=metallb \
  --timeout=90s

# Verify installation
kubectl get pods -n metallb-system
```

### Step 2: Configure IP Pool

```bash
# Create MetalLB configuration
cat << EOF > metallb-config.yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: k3s-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.1.240-192.168.1.250  # Adjust to your network range
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: k3s-l2
  namespace: metallb-system
spec:
  ipAddressPools:
  - k3s-pool
EOF

# Apply the configuration
kubectl apply -f metallb-config.yaml
```

### Step 3: Verify MetalLB Configuration

```bash
# Check MetalLB resources
kubectl get ipaddresspools -n metallb-system
kubectl get l2advertisements -n metallb-system

# Check MetalLB controller logs
kubectl logs -n metallb-system -l component=controller

# Check speaker logs
kubectl logs -n metallb-system -l component=speaker
```

## Testing the Installation

### Deploy Test Application

```bash
# Deploy the cluster-tester application
kubectl apply -f kubernetes/deploy.yaml

# Monitor deployment
kubectl get deployments -w

# Check service
kubectl get svc server-benchmark-service
```

### Verify LoadBalancer Service

```bash
# Get external IP (should be from MetalLB pool)
EXTERNAL_IP=$(kubectl get svc server-benchmark-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "Service available at: http://\$EXTERNAL_IP"

# Test the endpoints
curl http://\$EXTERNAL_IP/
curl http://\$EXTERNAL_IP/fibonacci/10
curl "http://\$EXTERNAL_IP/bubble-sort?n=1024"
```

## Advanced Configuration

### Custom K3s Configuration

```bash
# Create K3s configuration file
sudo mkdir -p /etc/rancher/k3s

cat << EOF | sudo tee /etc/rancher/k3s/config.yaml
cluster-cidr: "10.42.0.0/16"
service-cidr: "10.43.0.0/16"
disable:
  - servicelb
  - traefik  # Optional: disable if using external ingress
node-taint:
  - "node.kubernetes.io/unschedulable=true:NoExecute"  # Optional: master-only
EOF

# Restart K3s to apply configuration
sudo systemctl restart k3s
```

### High Availability Setup

```bash
# Install K3s server with embedded etcd (HA mode)
curl -sfL https://get.k3s.io | sh -s - server \
  --cluster-init \
  --disable=servicelb

# For additional servers in HA cluster
curl -sfL https://get.k3s.io | sh -s - server \
  --server https://<FIRST_SERVER_IP>:6443 \
  --token <CLUSTER_TOKEN> \
  --disable=servicelb
```

### Resource Limits and Requests

```bash
# Create resource quota for the default namespace
cat << EOF > resource-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
EOF

kubectl apply -f resource-quota.yaml
```

## Monitoring and Maintenance

### Useful K3s Commands

```bash
# Check K3s service status
sudo systemctl status k3s

# View K3s logs
sudo journalctl -u k3s -f

# Restart K3s
sudo systemctl restart k3s

# Check K3s version
k3s --version

# Upgrade K3s
curl -sfL https://get.k3s.io | sh -
```

### Cluster Health Checks

```bash
# Check node health
kubectl get nodes
kubectl describe nodes

# Check system pods
kubectl get pods -n kube-system

# Check resource usage
kubectl top nodes
kubectl top pods -A
```

## Troubleshooting

### Common Issues

**K3s not starting:**

```bash
# Check service status
sudo systemctl status k3s

# Check logs for errors
sudo journalctl -u k3s --no-pager -l

# Common fix: restart service
sudo systemctl restart k3s
```

**Worker nodes not joining:**

```bash
# Verify server connectivity
ping <server-ip>
curl -k https://<server-ip>:6443

# Check token validity
sudo cat /var/lib/rancher/k3s/server/node-token

# Verify firewall allows port 6443
sudo ufw allow 6443
```

**MetalLB not assigning IPs:**

```bash
# Check if ServiceLB is still running
kubectl get pods -n kube-system | grep svclb

# If found, ServiceLB conflicts with MetalLB
# Ensure --disable=servicelb was used during installation

# Check MetalLB speaker logs
kubectl logs -n metallb-system -l component=speaker

# Verify IP pool is in correct network range
ip route show
```

**Pods stuck in pending:**

```bash
# Check node resources
kubectl describe nodes

# Check pod events
kubectl describe pod <pod-name>

# Check for taints and tolerations
kubectl get nodes -o yaml | grep -A5 taints
```

## Backup and Recovery

### Backup K3s Data

```bash
# Backup K3s data directory
sudo cp -r /var/lib/rancher/k3s /backup/k3s-$(date +%Y%m%d)

# Backup kubeconfig
sudo cp /etc/rancher/k3s/k3s.yaml /backup/k3s-kubeconfig-$(date +%Y%m%d).yaml
```

### Restore from Backup

```bash
# Stop K3s service
sudo systemctl stop k3s

# Restore data directory
sudo rm -rf /var/lib/rancher/k3s
sudo cp -r /backup/k3s-20241110 /var/lib/rancher/k3s

# Start K3s service
sudo systemctl start k3s
```

## Uninstall K3s

```bash
# Run K3s uninstall script
/usr/local/bin/k3s-uninstall.sh

# For agent nodes
/usr/local/bin/k3s-agent-uninstall.sh

# Manual cleanup if needed
sudo rm -rf /var/lib/rancher/k3s
sudo rm -rf /etc/rancher/k3s
sudo rm /usr/local/bin/k3s
sudo rm /usr/local/bin/kubectl
```

## Next Steps

-   [Deploy the benchmark application](../../README.md#deploy-test-application)
-   [Configure cluster monitoring](../../README.md#configuration)
-   [Run your first benchmark](../../README.md#run-your-first-benchmark)
-   [Compare with other Kubernetes distributions](../../EXAMPLES.md#kubernetes-testing)
