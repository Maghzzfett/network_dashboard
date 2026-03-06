# This file contains the core logic for polling devices via SNMP,
# collecting metrics, and storing them in the database. It uses the OID mappings
from .oid_map import OID_MAP
from pysnmp.hlapi import (
    ObjectType, ObjectIdentity,
    getCmd, SnmpEngine,
    CommunityData, UdpTransportTarget,
    ContextData
)
from django.utils.timezone import now
from .models import Metric



def snmp_get(ip, oids, community="public"):
    """
    Query one or more OIDs from a device via SNMP.
    
    Args:
        ip (str): IP address of the device
        oids (list or str): OID(s) to query. Can be a single string or a list of strings.
        community (str): SNMP community string (default: "public")
    
    Returns:
        dict: Mapping of OID → value (float), or None if error
    """
    # Normalize input: always work with a list
    if isinstance(oids, str):
        oids = [oids]

    # Build ObjectTypes for each OID
    object_types = [ObjectType(ObjectIdentity(oid)) for oid in oids]

    # Send SNMP GET request
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip, 161)),
        ContextData(),
        *object_types  # unpack list of ObjectTypes
    )

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication or errorStatus:
        return None

    # Build dictionary of results
    results = {}
    for varBind in varBinds:
        oid, value = varBind
        results[str(oid)] = float(value)

    return results


def poll_device(device, prev_in=None, prev_out=None, prev_time=None):
    # --- Collect OIDs in one batch ---
    oids = [
        OID_MAP["uptime"]["standard"],
        OID_MAP["ifSpeed"]["standard"],
        OID_MAP["ifSpeed"]["highcapacity"],
        OID_MAP["ifInOctets"]["standard"],
        OID_MAP["ifOutOctets"]["standard"],
        OID_MAP["ifInOctets"]["highcapacity"],
        OID_MAP["ifOutOctets"]["highcapacity"],
    ]

    # Add vendor-specific CPU/Memory OIDs if available
    cpu_oid = OID_MAP["cpu_usage"].get(device.device_vendor)
    mem_oid = OID_MAP["memory_usage"].get(device.device_vendor)
    if cpu_oid:
        oids.append(cpu_oid)
    if mem_oid:
        oids.append(mem_oid)

    # Perform one SNMP GET for all OIDs
    results = snmp_get(device.ip_address, oids)

    if not results:
        return None, None, now()  # device unreachable or error

    # --- Uptime ---
    uptime_ticks = results.get(OID_MAP["uptime"]["standard"])
    if uptime_ticks is not None:
        Metric.objects.create(device=device, metric_type="uptime", value=uptime_ticks, unit="ticks")

    # --- Capacity (standard vs highcapacity) ---
    capacity_bps = results.get(OID_MAP["ifSpeed"]["standard"])
    if capacity_bps and capacity_bps < 100_000_000:
        # Old router (<100 Mbps) → prefer standard
        pass
    else:
        # Modern router (>1 Gbps) → prefer high-capacity
        capacity_mbps = results.get(OID_MAP["ifSpeed"]["highcapacity"])
        if capacity_mbps:
            capacity_bps = capacity_mbps * 1_000_000  # convert Mbps → bps

    Metric.objects.create(device=device, metric_name="capacity_bps", value=capacity_bps, unit="bps")

    # --- In/Out Octets (standard vs highcapacity) ---
    in_octets = results.get(OID_MAP["ifInOctets"]["standard"])
    out_octets = results.get(OID_MAP["ifOutOctets"]["standard"])

    if capacity_bps and capacity_bps < 100_000_000:
        # Old router (<100 Mbps) → prefer standard counters
        pass
    elif capacity_bps and capacity_bps >= 1_000_000_000:
        # Modern router (>1 Gbps) → prefer high-capacity counters
        in_octets = results.get(OID_MAP["ifInOctets"]["highcapacity"])
        out_octets = results.get(OID_MAP["ifOutOctets"]["highcapacity"])

    # --- Bandwidth Calculation ---
    if prev_in is not None and prev_out is not None and prev_time is not None:
        delta_t = (now() - prev_time).total_seconds()
        delta_in = (in_octets - prev_in) * 8 / delta_t
        delta_out = (out_octets - prev_out) * 8 / delta_t

        Metric.objects.create(device=device, metric_type="bandwidth_in", value=delta_in, unit="bps")
        Metric.objects.create(device=device, metric_type="bandwidth_out", value=delta_out, unit="bps")

    # --- CPU Usage ---
    if cpu_oid:
        cpu_value = results.get(cpu_oid)
        if cpu_value is not None:
            Metric.objects.create(device=device, metric_type="cpu_usage", value=cpu_value, unit="%")

    # --- Memory Usage ---
    if mem_oid:
        mem_value = results.get(mem_oid)
        if mem_value is not None:
            Metric.objects.create(device=device, metric_type="memory_usage", value=mem_value, unit="%")

    return in_octets, out_octets, now()