# DataForge

DataForge is a tool for generating data for testing and development purposes. It generates a set of CSV files which describe an imaginary but realistic dataset representing a VMware vSphere environment at a typical enterprise scale.

## Configuration

The environment generation can be customized through the `config/vsphere_config.yaml` file:

### Scale Options
Configure the overall size of the generated environment:
```yaml
scale:
  size: "large"  # Can be small, medium, large
  size_definitions:
    small:
      total_vms: 1000
      avg_vms_per_host: 20
      max_hosts_per_cluster: 12
    medium:
      total_vms: 5000
      avg_vms_per_host: 25
      max_hosts_per_cluster: 24
    large:
      total_vms: 20000
      avg_vms_per_host: 30
      max_hosts_per_cluster: 32
```

### Distribution Patterns
Configure how objects are distributed:
```yaml
distributions:
  cluster_sizes:
    large_site:  # For HQ regions
      tiny: {hosts: "4-8", weight: 0.1}    # Small dev/test clusters
      small: {hosts: "8-16", weight: 0.3}   # Standard workload clusters
      medium: {hosts: "16-24", weight: 0.4} # Main production clusters
      large: {hosts: "24-32", weight: 0.2}  # Large production clusters
```

### Regional Configuration
Define your vSphere regions:
```yaml
regions:
  HQ-A:
    weight: 0.3  # Proportion of total environment
    network_prefix: "10.10"
    datacenters: 2  # PROD and DR
    cluster_distribution: "large_site"
```

### Hardware and Software Options
Configure available hardware models and software versions:
```yaml
hosts:
  models:
    - name: "PowerEdge R750"
      weight: 0.6
      cpu_cores: 48
      memory_gb: 384

virtual_machines:
  os_types:
    - name: "Windows Server 2019 Standard"
      weight: 0.4
      typical_memory_gb: [8, 16, 32]
      typical_cpu_cores: [2, 4, 8]
```

See `config/vsphere_config.yaml` for the complete configuration options and examples.

## Generated Data Structure

The tool generates the following CSV files in the `vsphere-data` directory, organized in a hierarchical structure:

### Core Infrastructure
- **vCenters.csv** - vCenter Server instances
  - Contains vCenter server details including URL and version information
  - Parent to Datacenters

- **Datacenters.csv** - Virtual Datacenters
  - Contains datacenter configurations
  - Child of vCenter
  - Parent to Clusters
  - References: parent_vcenter → vCenters.moref

- **Clusters.csv** - Compute Clusters
  - Contains cluster configurations including HA/DRS settings
  - Child of Datacenter
  - Parent to ESXi Hosts
  - References: parent_datacenter → Datacenters.moref, parent_vcenter → vCenters.moref

### Compute Resources
- **ESXiHosts.csv** - ESXi Host servers
  - Contains physical server specifications and status
  - Child of Cluster
  - Parent to VMs and HostNICs
  - References: parent_cluster → Clusters.moref, parent_datacenter → Datacenters.moref

- **HostNICs.csv** - Physical Network Interface Cards
  - Contains NIC configurations for ESXi hosts
  - Child of ESXi Host
  - References: parent_host → ESXiHosts.moref

### Virtual Machines
- **VirtualMachines.csv** - Virtual Machine instances
  - Contains VM configurations and specifications
  - Child of ESXi Host
  - References: parent_host → ESXiHosts.moref, cluster_moref → Clusters.moref

- **VMGuestDetails.csv** - Guest OS details
  - Contains guest operating system information and metrics
  - Child of Virtual Machine
  - References: vm_moref → VirtualMachines.moref

### Storage
- **Datastores.csv** - Storage volumes
  - Contains storage specifications and usage
  - Child of Cluster
  - References: parent_cluster → Clusters.moref, datastore_cluster → DatastoreClusters.moref

- **DatastoreClusters.csv** - Storage DRS clusters
  - Contains storage cluster configurations
  - Child of Cluster
  - Parent to Datastores
  - References: parent_cluster → Clusters.moref

### Networking
- **VirtualSwitches.csv** - Virtual networking switches
  - Contains virtual switch configurations
  - Parent to Port Groups and Networks
  - Associated with Datacenter level

- **Networks.csv** - Network definitions
  - Contains network configurations and IP ranges
  - Child of Virtual Switch
  - References: parent_vswitch → VirtualSwitches.moref

- **PortGroups.csv** - Network port groups
  - Contains port group configurations and policies
  - Child of Virtual Switch
  - References: parent_vswitch → VirtualSwitches.moref

### Tags and Metadata
- **NSXTags.csv** - NSX-T tags
  - Contains object tagging information
  - References: object_moref → various .moref fields depending on object_type

## Usage

```bash
python3 generate-vsphere.py
```

This will generate all CSV files in the `vsphere-data` directory. The data is generated with realistic relationships and configurations that mirror typical enterprise VMware deployments.

## Data Relationships

The generated data follows VMware's typical hierarchy:
```
vCenter
└── Datacenter
    ├── Clusters
    │   ├── ESXi Hosts
    │   │   ├── Virtual Machines
    │   │   └── Host NICs
    │   └── Datastore Clusters
    │       └── Datastores
    └── Networking
        ├── Virtual Switches
        ├── Port Groups
        └── Networks
```

Each object maintains referential integrity through moref (Managed Object Reference) IDs that link to their parent objects.