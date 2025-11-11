# MicroK8s Setup Guide

MicroK8s is a lightweight Kubernetes distribution that's perfect for development, testing, and small-scale production deployments.

## Prerequisites

-   Ubuntu 18.04 or later
-   At least 4GB RAM
-   20GB disk space
-   Root or sudo access

## Installation

### Step 1: Install Snap Package Manager

```bash
# Update package list
sudo apt update

# Install snapd if not already installed
sudo apt install snapd

# Install core snap
sudo snap install core
```

### Step 2: Install MicroK8s

```bash
# Install MicroK8s (latest stable channel)
sudo snap install microk8s --classic --channel=1.33

# Add current user to microk8s group
sudo usermod -a -G microk8s $USER

# Create kubectl config directory
mkdir -p ~/.kube
chmod 0700 ~/.kube

# Apply group changes (logout/login or use newgrp)
newgrp microk8s

# Wait for MicroK8s to be ready
microk8s status --wait-ready
```

### Step 3: Verify Installation

```bash
# Check cluster status
microk8s status

# List nodes
microk8s kubectl get nodes

# Check running pods
microk8s kubectl get pods -A
```

## Configure kubectl Access

```bash
# Create kubectl config
microk8s kubectl config view --raw > ~/.kube/config

# Or use microk8s alias
echo 'alias kubectl="microk8s kubectl"' >> ~/.bashrc
source ~/.bashrc
```

## Enable Required Add-ons

### Enable MetalLB for LoadBalancer Services

```bash
# Enable MetalLB
microk8s enable metallb

# You'll be prompted for an IP address range
# Example: 192.168.1.240-192.168.1.250
```

### Enable Other Useful Add-ons

```bash
# Enable DNS (usually enabled by default)
microk8s enable dns

# Enable storage
microk8s enable storage

# Enable dashboard (optional)
microk8s enable dashboard

# Enable registry (optional)
microk8s enable registry

# List all available add-ons
microk8s status
```

## Advanced Configuration

### Custom MetalLB Configuration

If you need to reconfigure MetalLB after installation:

```bash
# Create MetalLB configuration
cat << EOF > metallb-config.yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: microk8s-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.1.240-192.168.1.250  # Adjust to your network
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: microk8s-l2
  namespace: metallb-system
spec:
  ipAddressPools:
  - microk8s-pool
EOF

# Apply configuration
microk8s kubectl apply -f metallb-config.yaml
```

### Multi-node Setup

To add worker nodes to your MicroK8s cluster:

```bash
# On the main node, generate join token
microk8s add-node

# On worker node, use the provided command
microk8s join <main-node-ip>:25000/<token>
```

## Testing the Installation

### Deploy Test Application

```bash
# Deploy the cluster-tester application
microk8s kubectl apply -f kubernetes/deploy.yaml

# Check deployment
microk8s kubectl get deployments
microk8s kubectl get services
microk8s kubectl get pods

# Get external IP (MetalLB assigned)
microk8s kubectl get svc server-benchmark-service
```

### Access Application

```bash
# Get service external IP
EXTERNAL_IP=$(microk8s kubectl get svc server-benchmark-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test endpoints
curl "http://${EXTERNAL_IP}/"
curl "http://${EXTERNAL_IP}/fibonacci/10"
```

## Troubleshooting

### Common Issues

**MicroK8s not starting:**

```bash
# Check snap services
sudo systemctl status snap.microk8s.daemon-cluster-agent
sudo systemctl status snap.microk8s.daemon-containerd

# Restart MicroK8s
microk8s stop
microk8s start
```

**Permission denied errors:**

```bash
# Ensure user is in microk8s group
groups $USER

# If not in group, add and re-login
sudo usermod -a -G microk8s $USER
su - $USER
```

**MetalLB not assigning IPs:**

```bash
# Check MetalLB configuration
microk8s kubectl get ipaddresspools -n metallb-system
microk8s kubectl get l2advertisements -n metallb-system

# Check MetalLB logs
microk8s kubectl logs -n metallb-system -l app=metallb
```

## Uninstall

```bash
# Stop MicroK8s
microk8s stop

# Remove snap
sudo snap remove microk8s

# Clean up remaining files (optional)
sudo rm -rf /var/snap/microk8s
```

## Next Steps

-   [Deploy the benchmark application](../../README.md#deploy-test-application)
-   [Configure cluster monitoring](../../README.md#configuration)
-   [Run your first benchmark](../../README.md#run-your-first-benchmark)
