import subprocess # For executing system commands
import platform # for detecting the running OS
from datetime import datetime # For timestamping logs
import re # For parsing command output

def ping_device(ip_address):
    """
    Ping a device and return True if reachable, else False.
    Handles timeouts explicitly.
    """
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', ip_address]

    try:
        result = subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            timeout=5 # wait max 5 sec
        )
        output = result.stdout.lower()
        # check for successful keywords in output
        if 'ttl=' in output or 'bytes=' in output:
            return True
        # check for failure keywords in output
        if 'request timed out' in output or 'unreachable' in output or 'could not find host' in output:
            return False
        # Fallback: use return code if output is ambiguous
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        # if ping takes longer than timeout, consider it offline
        return False
    except Exception as e:
        return f"Exception occurred: {str(e)}"

def traceroute_device(ip_address, max_hops=30):
    """
    Run traceroute (Linux/macOS) or tracert (Windows) to a device.
    Returns parsed hops with IPs and latencies.
    """
    system = platform.system().lower()
    if system == 'windows':
        command = ['tracert', '-d', '-h', str(max_hops), ip_address]
    else:
        command = ['traceroute', '-I', '-n', '-m', str(max_hops), ip_address]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return {"error": result.stderr.strip()}

        hops = []
        for line in result.stdout.splitlines():
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
            ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
            ip = ip_match.group(1) if ip_match else None

            # Extract all latency samples
            latencies = re.findall(r"(\d+\.\d+)\s*ms", line)
            latencies = [float(l) for l in latencies] if latencies else []

            hops.append({
                "hop": hop_number,
                "ip": ip,
                "latency_ms": latencies,
                "status": "ok" if ip else "unknown"
            })

        return {"destination": ip_address, "hops": hops}

    except subprocess.TimeoutExpired:
        return {"error": "Traceroute timed out"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}