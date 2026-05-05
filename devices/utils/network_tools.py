import subprocess  # For executing system commands
import platform  # for detecting the running OS
from datetime import datetime  # For timestamping logs
import re  # For parsing command output
from .constants import PING_TIMEOUT, TRACEROUTE_TIMEOUT, DEFAULT_MAX_HOPS


class PingException(Exception):
    """Custom exception for ping failures"""
    pass


class TracerouteException(Exception):
    """Custom exception for traceroute failures"""
    pass


def get_platform_type():
    """Return 'windows' or 'unix' based on running OS"""
    return 'windows' if platform.system().lower() == 'windows' else 'unix'


def ping_device(ip_address, timeout=PING_TIMEOUT):
    """
    Ping a device and return True if reachable, else False.
    
    Args:
        ip_address (str): IP address to ping
        timeout (int): Timeout in seconds
    
    Returns:
        bool: True if reachable, False otherwise
    
    Raises:
        PingException: If ping command fails
    """
    param = '-n' if get_platform_type() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]

    try:
        result = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        output = result.stdout.lower()
        # Check for successful keywords in output
        if 'ttl=' in output or 'bytes=' in output:
            return True
        # Check for failure keywords in output
        if 'request timed out' in output or 'unreachable' in output or 'could not find host' in output:
            return False
        # Fallback: use return code if output is ambiguous
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception as e:
        raise PingException(f"Ping to {ip_address} failed: {str(e)}")

def traceroute_device(ip_address, max_hops=DEFAULT_MAX_HOPS, timeout=TRACEROUTE_TIMEOUT):
    """
    Run traceroute (Linux/macOS) or tracert (Windows) to a device.
    
    Args:
        ip_address (str): IP address to trace
        max_hops (int): Maximum hops to trace
        timeout (int): Timeout in seconds
    
    Returns:
        dict: Dictionary with destination and hops information
    
    Raises:
        TracerouteException: If traceroute command fails
    """
    platform_type = get_platform_type()
    if platform_type == 'windows':
        command = ['tracert', '-d', '-h', str(max_hops), ip_address]
    else:
        command = ['traceroute', '-I', '-n', '-m', str(max_hops), ip_address]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            raise TracerouteException(result.stderr.strip())

        return parse_traceroute_output(result.stdout, ip_address)

    except subprocess.TimeoutExpired:
        raise TracerouteException(f"Traceroute to {ip_address} timed out")
    except TracerouteException:
        raise
    except Exception as e:
        raise TracerouteException(f"Traceroute to {ip_address} failed: {str(e)}")


def parse_traceroute_output(output, destination):
    """
    Parse traceroute command output into structured data.
    
    Args:
        output (str): Raw output from traceroute command
        destination (str): Target IP address
    
    Returns:
        dict: Structured traceroute data with hops
    """
    hops = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        # Match hop number at start
        hop_match = re.match(r"^(\d+)", line)
        if not hop_match:
            continue

        hop_number = int(hop_match.group(1))

        # Handle timeout lines (* * *)
        if "*" in line:
            hops.append({
                "hop": hop_number,
                "ip": None,
                "latency_ms": None,
                "status": "timeout"
            })
            continue

        # Extract IP address
        ip = None
        ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
        if ip_match:
            ip = ip_match.group(1)

        # Extract all latency samples
        latencies = [float(l) for l in re.findall(r"(\d+\.\d+)\s*ms", line)]

        hops.append({
            "hop": hop_number,
            "ip": ip,
            "latency_ms": latencies,
            "status": "ok" if ip else "unknown"
        })

    return {"destination": destination, "hops": hops}