# DataForge

DataForge is a tool for generating data for testing and development purposes. It can currently generate a set of csv files which describe an imaginary but realistic dataset describing a VMware vSphere environment at a typical enterprise scale.

## Generated Data

The tool generates the following CSV files in the `vsphere-data` directory:
- vCenters.csv - vCenter Server instances with URLs and version information
- Datacenters.csv - Virtual Datacenters associated with vCenters
- Clusters.csv
- DatastoreClusters.csv
- Datastores.csv
- ESXiHosts.csv
- HostNICs.csv
- Networks.csv
- PortGroups.csv
- VirtualMachines.csv
- VMGuestDetails.csv
- VirtualSwitches.csv
- NSXTags.csv

## Usage

```bash
python3 generate-vsphere.py
```

This will generate the CSV files in the `vsphere-data` directory.