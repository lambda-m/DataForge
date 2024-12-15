import csv
import random
from datetime import datetime, timedelta
import ipaddress
import uuid
from typing import List, Dict
import itertools
import os
import shutil
from urllib.parse import urlparse

class VSphereEnvironmentGenerator:
    def __init__(self):
        # Core infrastructure components
        self.vcenters: List[Dict] = []
        self.datacenters: List[Dict] = []
        self.clusters: List[Dict] = []
        self.hosts: List[Dict] = []
        self.vms: List[Dict] = []
        self.datastores: List[Dict] = []
        self.datastore_clusters: List[Dict] = []
        self.networks: List[Dict] = []
        self.portgroups: List[Dict] = []
        self.nsx_tags: List[Dict] = []
        self.host_nics: List[Dict] = []
        self.vm_guest_details: List[Dict] = []
        self.virtual_switches: List[Dict] = []

        # Configuration constants
        self.REGIONS = {
            'HQ-A': {'weight': 0.3, 'network_prefix': '10.10'},
            'HQ-B': {'weight': 0.3, 'network_prefix': '10.20'},
            'NA': {'weight': 0.15, 'network_prefix': '10.30'},
            'EU': {'weight': 0.15, 'network_prefix': '10.40'},
            'APAC': {'weight': 0.1, 'network_prefix': '10.50'}
        }

        self.OS_TYPES = {
            'Windows Server 2019 Standard': 0.4,
            'Windows Server 2022 Standard': 0.3,
            'RHEL 8.6': 0.15,
            'Ubuntu 20.04 LTS': 0.15
        }

        self.VM_PURPOSES = ['WEB', 'APP', 'DB', 'SVC', 'MON', 'INF']
        self.start_date = datetime(2019, 1, 1)
        self.end_date = datetime.now()

        # Ensure clean output directory
        self.output_dir = "vsphere-data"
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

    def generate_moref(self, prefix: str, num: int) -> str:
        return f"{prefix}-{num:06d}"

    def generate_mac_address(self) -> str:
        return f"00:50:56:{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}"

    def random_date(self) -> datetime:
        time_between_dates = self.end_date - self.start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        return self.start_date + timedelta(days=random_number_of_days)

    def get_full_region_name(self, vcenter_name: str) -> str:
        region = vcenter_name.split('-')[0]
        if region == 'HQ':
            return f"{region}-{vcenter_name.split('-')[1]}"
        return region

    def generate_vcenters(self):
        print("Generating vCenters...")
        for region in self.REGIONS:
            vcenter = {
                'name': f"{region}-VC-01",
                'moref': f"vc-{uuid.uuid4().hex[:8]}",
                'version': "7.0.3g",
                'build': "20150588",
                'url': f"https://{region.lower()}-vc-01.vsphere.local",
                'description': f"{region} vCenter, deployed 2021"
            }
            self.vcenters.append(vcenter)

    def generate_clusters(self):
        print("Generating Clusters...")
        cluster_id = 1000
        for datacenter in self.datacenters:
            vcenter = next(vc for vc in self.vcenters if vc['moref'] == datacenter['parent_vcenter'])
            region = self.get_full_region_name(vcenter['name'])
            
            # Determine number of clusters based on datacenter purpose
            num_clusters = 30 if region.startswith('HQ') else 7
            
            for i in range(num_clusters):
                cluster = {
                    'name': f"{region}-CL-{i+1:02d}",
                    'moref': f"domain-c{cluster_id}",
                    'parent_datacenter': datacenter['moref'],
                    'parent_vcenter': datacenter['parent_vcenter'],
                    'total_hosts': random.randint(4, 12),
                    'total_vms': random.randint(40, 120),
                    'total_cpu_cores': 0,
                    'total_memory': 0,
                    'ha_enabled': True,
                    'drs_enabled': True,
                    'notes': f"Cluster for {region} workloads"
                }
                self.clusters.append(cluster)
                cluster_id += 1

    def generate_hosts(self):
        print("Generating ESXi Hosts...")
        host_id = 1000
        for cluster in self.clusters:
            datacenter = next(dc for dc in self.datacenters if dc['moref'] == cluster['parent_datacenter'])
            for i in range(cluster['total_hosts']):
                host = {
                    'name': f"{cluster['name'].replace('CL', 'ESX')}-{i+1:02d}",
                    'moref': f"host-{host_id}",
                    'parent_cluster': cluster['moref'],
                    'parent_datacenter': datacenter['moref'],
                    'vcenter_moref': cluster['parent_vcenter'],
                    'cpu_cores': 48,
                    'memory_gb': 384,
                    'nic_count': 8,
                    'datastores_count': 12,
                    'status': random.choice(['Connected'] * 95 + ['Maintenance'] * 5),
                    'model': random.choice(['PowerEdge R750', 'PowerEdge R840']),
                    'vendor': 'Dell',
                    'serial': f"DELL{random.randint(100000,999999)}",
                    'uptime': random.uniform(100, 400)
                }
                self.hosts.append(host)
                self.generate_host_nics(host)
                host_id += 1

    def generate_datastores(self):
        print("Generating Datastores...")
        datastore_id = 1000
        for cluster in self.clusters:
            for i in range(random.randint(4, 8)):
                capacity = random.choice([2048, 4096, 8192, 16384])
                free_space = int(capacity * random.uniform(0.2, 0.4))
                provisioned = int(capacity * random.uniform(0.7, 0.9))
                
                datastore = {
                    'name': f"{cluster['name'].replace('CL', 'DS')}-{i+1:02d}",
                    'moref': f"datastore-{datastore_id}",
                    'parent_cluster': cluster['moref'],
                    'type': random.choice(['VMFS-6'] * 8 + ['NFS'] * 2),
                    'capacity_gb': capacity,
                    'free_space_gb': free_space,
                    'provisioned_space_gb': provisioned,
                    'datastore_cluster': f"DSC-{cluster['name']}-01",
                    'storage_array': random.choice(['PowerStore', 'Unity XT']),
                    'storage_model': random.choice(['PowerStore T1000', 'Unity XT 880']),
                    'storage_serial': f"PS{random.randint(10000,99999)}"
                }
                self.datastores.append(datastore)
                datastore_id += 1

    def generate_datastore_clusters(self):
        print("Generating Datastore Clusters...")
        dsc_id = 1000
        for cluster in self.clusters:
            cluster_datastores = [ds for ds in self.datastores if ds['parent_cluster'] == cluster['moref']]
            if cluster_datastores:
                dsc = {
                    'name': f"DSC-{cluster['name']}-01",
                    'moref': f"dsc-{dsc_id}",
                    'parent_cluster': cluster['moref'],
                    'total_capacity_gb': sum(ds['capacity_gb'] for ds in cluster_datastores),
                    'free_space_gb': sum(ds['free_space_gb'] for ds in cluster_datastores),
                    'total_datastores': len(cluster_datastores),
                    'sdrs_enabled': True,
                    'automation_level': random.choice(['Fully Automated', 'Manual']),
                    'space_threshold': random.randint(75, 85)
                }
                self.datastore_clusters.append(dsc)
                dsc_id += 1

    def generate_virtual_switches(self):
        print("Generating Virtual Switches...")
        switch_id = 1000
        for vcenter in self.vcenters:
            region = self.get_full_region_name(vcenter['name'])
            switch = {
                'name': f"{region}-DVS-01",
                'moref': f"dvs-{switch_id}",
                'type': 'Distributed',
                'uplinks': 4,
                'port_groups': 0,  # Will be updated later
                'mtu': 9000,
                'load_balancing': "Route based on physical NIC load",
                'notes': f"Main distributed switch for {region}"
            }
            self.virtual_switches.append(switch)
            switch_id += 1

    def generate_vms(self):
        print("Generating Virtual Machines...")
        vm_id = 1000
        for cluster in self.clusters:
            vcenter = next(vc for vc in self.vcenters if vc['moref'] == cluster['parent_vcenter'])
            region = self.get_full_region_name(vcenter['name'])
            network_prefix = self.REGIONS[region]['network_prefix']
            
            for i in range(cluster['total_vms']):
                purpose = random.choice(self.VM_PURPOSES)
                os_type = random.choices(list(self.OS_TYPES.keys()), 
                                      list(self.OS_TYPES.values()))[0]
                
                vm = {
                    'name': f"{region}-VM-{purpose}-{vm_id:04d}",
                    'moref': f"vm-{vm_id}",
                    'parent_host': random.choice([h['moref'] for h in self.hosts if h['parent_cluster'] == cluster['moref']]),
                    'cluster_moref': cluster['moref'],
                    'vcenter_moref': cluster['parent_vcenter'],
                    'guest_os': os_type,
                    'vm_version': f"v{random.randint(14,19)}",
                    'cpu_count': random.choice([2,4,8,16]),
                    'memory_gb': random.choice([4,8,16,32,64,128]),
                    'disk_count': random.randint(1,4),
                    'nic_count': random.randint(1,4),
                    'ip_addresses': f"{network_prefix}.{random.randint(1,254)}.{random.randint(1,254)}",
                    'power_state': random.choice(['poweredOn'] * 90 + ['poweredOff'] * 10),
                    'created_date': self.random_date(),
                    'notes': f"{purpose} workload"
                }
                self.vms.append(vm)
                self.generate_vm_guest_details(vm)
                vm_id += 1

    def generate_vm_guest_details(self, vm: Dict):
        guest_detail = {
            'vm_moref': vm['moref'],
            'guest_os_full': vm['guest_os'],
            'ip_addresses': vm['ip_addresses'],
            'hostname': vm['name'].lower(),
            'uptime': random.uniform(1, 400),
            'tools_status': 'Running Current',
            'tools_version': '12365',
            'guest_state': 'Running' if vm['power_state'] == 'poweredOn' else 'Stopped',
            'cpu_usage': random.randint(20, 80),
            'memory_usage': random.randint(40, 90),
            'notes': vm['notes']
        }
        self.vm_guest_details.append(guest_detail)

    def generate_host_nics(self, host: Dict):
        for i in range(host['nic_count']):
            nic = {
                'name': f"vmnic{i}",
                'moref': f"nic-{host['moref']}-{i}",
                'parent_host': host['moref'],
                'mac_address': self.generate_mac_address(),
                'link_status': random.choice(['Up'] * 95 + ['Down'] * 5),
                'speed': random.choice([10000, 25000, 40000]),
                'duplex': 'Full',
                'driver': 'vmxnet3',
                'firmware': f"1.{random.randint(1,9)}.{random.randint(0,9)}",
                'pci_address': f"0000:{random.randint(0,99):02d}:00.{i}",
                'notes': f"NIC {i+1} for host {host['name']}"
            }
            self.host_nics.append(nic)

    def generate_networks(self):
        print("Generating Networks and Port Groups...")
        network_id = 1000
        for vcenter in self.vcenters:
            region = self.get_full_region_name(vcenter['name'])
            network_prefix = self.REGIONS[region]['network_prefix']
            
            for purpose in ['PROD', 'DEV', 'DMZ', 'MGMT']:
                for segment in ['WEB', 'APP', 'DB']:
                    network = {
                        'name': f"{region}-NET-{purpose}-{segment}",
                        'moref': f"network-{network_id}",
                        'parent_vswitch': f"dvs-{region}-01",
                        'ip_range': f"{network_prefix}.{network_id % 255}.0/24",
                        'subnet_mask': "255.255.255.0",
                        'gateway': f"{network_prefix}.{network_id % 255}.1",
                        'associated_vms': ','.join([vm['moref'] for vm in self.vms if vm['name'].split('-')[2] == segment][:5]),
                        'purpose': purpose,
                        'vlan_id': network_id,
                        'notes': f"{purpose} {segment} network"
                    }
                    self.networks.append(network)
                    self.generate_portgroup(network)
                    network_id += 1

    def generate_portgroup(self, network: Dict):
        portgroup = {
            'name': f"PG-{network['name']}",
            'moref': f"pg-{network['moref'].split('-')[1]}",
            'parent_vswitch': network['parent_vswitch'],
            'vlan_id': network['vlan_id'],
            'associated_vms': network['associated_vms'],
            'security_policy': "Promiscuous:Reject;Forged:Reject",
            'traffic_shaping': "Disabled",
            'teaming_policy': "Active:uplink1,uplink2;Standby:uplink3,uplink4",
            'notes': network['notes']
        }
        self.portgroups.append(portgroup)

    def generate_nsx_tags(self):
        print("Generating NSX Tags...")
        tag_id = 1000
        tag_categories = ['Environment', 'Application', 'Security', 'Compliance']
        
        for category in tag_categories:
            for vm in random.sample(self.vms, len(self.vms) // 4):
                tag = {
                    'name': f"TAG-{category}-{tag_id}",
                    'moref': f"tag-{tag_id}",
                    'object_type': 'VM',
                    'object_moref': vm['moref'],
                    'category': category,
                    'value': vm['notes'].split()[0],
                    'created_date': vm['created_date'].strftime('%Y-%m-%d'),
                    'modified_date': self.end_date.strftime('%Y-%m-%d'),
                    'notes': f"{category} tag for {vm['name']}"
                }
                self.nsx_tags.append(tag)
                tag_id += 1

    def export_to_csv(self):
        print(f"Exporting data to {self.output_dir}/...")
        csv_files = {
            'vCenters.csv': (self.vcenters, ['name', 'moref', 'version', 'build', 'url', 'description']),
            'Datacenters.csv': (self.datacenters, ['name', 'moref', 'parent_vcenter', 'description', 'status']),
            'Clusters.csv': (self.clusters, ['name', 'moref', 'parent_datacenter', 'parent_vcenter', 'total_hosts', 'total_vms', 'total_cpu_cores', 'total_memory', 'ha_enabled', 'drs_enabled', 'notes']),
            'ESXiHosts.csv': (self.hosts, ['name', 'moref', 'parent_cluster', 'vcenter_moref', 'cpu_cores', 'memory_gb', 'nic_count', 'datastores_count', 'status', 'model', 'vendor', 'serial', 'uptime']),
            'VirtualMachines.csv': (self.vms, ['name', 'moref', 'parent_host', 'cluster_moref', 'vcenter_moref', 'guest_os', 'vm_version', 'cpu_count', 'memory_gb', 'disk_count', 'nic_count', 'ip_addresses', 'power_state', 'created_date', 'notes']),
            'VMGuestDetails.csv': (self.vm_guest_details, ['vm_moref', 'guest_os_full', 'ip_addresses', 'hostname', 'uptime', 'tools_status', 'tools_version', 'guest_state', 'cpu_usage', 'memory_usage', 'notes']),
            'Datastores.csv': (self.datastores, ['name', 'moref', 'parent_cluster', 'type', 'capacity_gb', 'free_space_gb', 'provisioned_space_gb', 'datastore_cluster', 'storage_array', 'storage_model', 'storage_serial']),
            'DatastoreClusters.csv': (self.datastore_clusters, ['name', 'moref', 'parent_cluster', 'total_capacity_gb', 'free_space_gb', 'total_datastores', 'sdrs_enabled', 'automation_level', 'space_threshold']),
            'VirtualSwitches.csv': (self.virtual_switches, ['name', 'moref', 'type', 'uplinks', 'port_groups', 'mtu', 'load_balancing', 'notes']),
            'Networks.csv': (self.networks, ['name', 'moref', 'parent_vswitch', 'ip_range', 'subnet_mask', 'gateway', 'associated_vms', 'purpose', 'vlan_id', 'notes']),
            'PortGroups.csv': (self.portgroups, ['name', 'moref', 'parent_vswitch', 'vlan_id', 'associated_vms', 'security_policy', 'traffic_shaping', 'teaming_policy', 'notes']),
            'NSXTags.csv': (self.nsx_tags, ['name', 'moref', 'object_type', 'object_moref', 'category', 'value', 'created_date', 'modified_date', 'notes']),
            'HostNICs.csv': (self.host_nics, ['name', 'moref', 'parent_host', 'mac_address', 'link_status', 'speed', 'duplex', 'driver', 'firmware', 'pci_address', 'notes'])
        }

        for filename, (data, fields) in csv_files.items():
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields)
                writer.writeheader()
                for row in data:
                    writer.writerow({field: row[field] for field in fields})

    def generate_all(self):
        print("Starting vSphere environment data generation...")
        self.generate_vcenters()
        self.generate_datacenters()
        self.generate_clusters()
        self.generate_hosts()
        self.generate_datastores()
        self.generate_datastore_clusters()
        self.generate_virtual_switches()
        self.generate_vms()
        self.generate_networks()
        self.generate_nsx_tags()
        self.export_to_csv()
        print("Data generation complete!")

    def generate_datacenters(self):
        print("Generating Datacenters...")
        for vcenter in self.vcenters:
            region = self.get_full_region_name(vcenter['name'])
            # HQ regions get 2 datacenters, others get 1
            num_dcs = 2 if region.startswith('HQ') else 1
            
            for i in range(num_dcs):
                purpose = 'PROD' if i == 0 else 'DR'
                datacenter = {
                    'name': f"{region}-DC-{purpose}",
                    'moref': f"datacenter-{uuid.uuid4().hex[:8]}",
                    'parent_vcenter': vcenter['moref'],
                    'description': f"{purpose} Datacenter for {region}",
                    'status': 'Available'
                }
                self.datacenters.append(datacenter)

def generate_vcenter_url(vcenter_name):
    # Convert name to lowercase and remove spaces for hostname
    hostname = vcenter_name.lower().replace(' ', '')
    # Add realistic domain and format as proper vCenter URL
    return f"https://{hostname}.vsphere.local"

def generate_datacenters(num_datacenters, vcenter_ids):
    datacenters = []
    dc_names = [f"Datacenter-{i+1}" for i in range(num_datacenters)]
    
    for vcenter_id in vcenter_ids:
        # Each vCenter gets 1-3 datacenters
        num_dcs = random.randint(1, 3)
        for i in range(num_dcs):
            dc_id = str(uuid.uuid4())
            name = f"DC-{random.choice(['PROD', 'DEV', 'TEST', 'DR'])}-{random.randint(1,99)}"
            description = f"Virtual Datacenter for {name}"
            datacenters.append([name, dc_id, vcenter_id, description])
    
    return datacenters

def generate_vcenters(num_vcenters):
    vcenters = []
    versions = ['7.0.3', '8.0.0', '8.0.1']
    builds = ['20150588', '20519528', '20802592']
    
    for i in range(num_vcenters):
        vcenter_id = str(uuid.uuid4())
        name = f"vcenter-{random.randint(1,999):03d}"
        url = generate_vcenter_url(name)
        version = random.choice(versions)
        build = random.choice(builds)
        vcenters.append([name, vcenter_id, url, version, build])
    
    return vcenters

def generate_vsphere_data():
    # ... existing code ...
    
    # Generate vCenters first
    vcenters = generate_vcenters(num_vcenters)
    vcenter_ids = [vc[1] for vc in vcenters]
    
    # Generate datacenters before other objects
    datacenters = generate_datacenters(num_datacenters, vcenter_ids)
    
    # Write the new datacenter data
    write_csv('vsphere-data/Datacenters.csv', 
             ['Name', 'ID', 'vCenterID', 'Description'], 
             datacenters)
    
    # Modify the vCenter CSV writing to match new structure
    write_csv('vsphere-data/vCenters.csv',
             ['Name', 'ID', 'URL', 'Version', 'Build'],
             vcenters)
    
    # ... rest of your existing code ...

if __name__ == "__main__":
    generator = VSphereEnvironmentGenerator()
    generator.generate_all()