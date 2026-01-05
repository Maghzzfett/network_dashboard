import subprocess # For executing system commands
import platform # for detecting the running OS
from datetime import datetime # For timestamping logs
import re # For parsing command output

def ping_device(ip_address):
    """
    Ping a device and return True if reachable, else False.
    """
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', ip_address]

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error pinging device: {result.stderr}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"
    
def traceroute_device(ip_address, max_hops=30):
    """
    Run traceroute (Linux/macOS) or tracert (Windows) to a device.
    Returns the raw output as a string.
    """
    system = platform.system().lower()
    if system == 'windows':
        command = ['tracert', '-d', '-h', str(max_hops), ip_address]
    else:
        command = ['traceroute', '-n', '-m', str(max_hops), ip_address]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return {"error": result.stderr}

        hops = []
        for line in result.stdout.splitlines():
            # Match hop lines: hop_number, IP, latency
            match = re.match(r"^\s*(\d+)\s+([\d\.]+)\s+(\d+\.\d+)\s+ms", line)
            if match:
                hop_number = int(match.group(1))
                ip = match.group(2)
                latency = float(match.group(3))
                hops.append({
                    "hop": hop_number,
                    "ip": ip,
                    "latency_ms": latency
                })

        return {"destination": ip_address, "hops": hops}

    except Exception as e:
        return f"Exception occurred: {str(e)}"
    