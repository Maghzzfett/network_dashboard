OID_MAP = {
    # Vendor-specific OIDs for bandwidth and uptime
    "cpu_usage": {
        "cisco": "1.3.6.1.4.1.9.2.1.57.0",
        "juniper": "1.3.6.1.4.1.2636.3.1.13.1.8.0",
        "mikrotik": "1.3.6.1.4.1.14988.1.1.7.4.0"
    },
    "memory_usage": {
        "cisco": "1.3.6.1.4.1.9.9.305.1.1.2.0",
        "juniper": "1.3.6.1.4.1.2636.3.1.13.1.11.0",
        "mikrotik": "1.3.6.1.4.1.14988.1.1.7.6.0"
    },

    #standard OIDs for bandwidth and uptime
    "uptime": {
        "standard": "1.3.6.1.2.1.1.3.0"  # sysUpTime
    },
    "ifSpeed": {
        "standard": "1.3.6.1.2.1.2.2.1.5", # 100 Mbps or less
        "highspeed": "1.3.6.1.2.1.31.1.1.1.15" # 1 Gbps or more
    },
    "ifInOctets": {
        "standard": "1.3.6.1.2.1.2.2.1.10",
        "highcapacity": "1.3.6.1.2.1.31.1.1.1.6"
    },
    "ifOutOctets": {
        "standard": "1.3.6.1.2.1.2.2.1.16",
        "highcapacity": "1.3.6.1.2.1.31.1.1.1.10"
    }
    
}