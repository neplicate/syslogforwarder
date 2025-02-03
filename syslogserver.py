import json
import socket
import os
import time
from datetime import datetime

def load_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    # Validate required keys
    required_keys = ['server_ip', 'server_port', 'log_file']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    # Set defaults for optional keys
    config.setdefault('protocol', 'udp')
    config.setdefault('facility', 1)
    config.setdefault('severity', 6)
    config.setdefault('app_name', 'syslog_forwarder')
    return config

def create_syslog_message(log_line, config):
    pri = config['facility'] * 8 + config['severity']
    version = 1
    timestamp = datetime.utcnow().isoformat() + 'Z'
    hostname = socket.gethostname()
    app_name = config['app_name']
    pid = os.getpid()
    return f"<{pri}>{version} {timestamp} {hostname} {app_name} {pid} - - {log_line}"

def main():
    config = load_config('config.json')
    server_ip = config['server_ip']
    server_port = config['server_port']
    protocol = config['protocol'].lower()
    log_file = config['log_file']

    # Setup socket
    if protocol == 'udp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    elif protocol == 'tcp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((server_ip, server_port))
        except Exception as e:
            print(f"TCP connection error: {e}")
            return
    else:
        raise ValueError("Invalid protocol. Use 'udp' or 'tcp'.")

    try:
        with open(log_file, 'r') as f:
            # Move to the end of the file
            f.seek(0, os.SEEK_END)
            while True:
                current_pos = f.tell()
                line = f.readline()
                if not line:
                    # Check if file was truncated
                    if os.path.getsize(log_file) < current_pos:
                        f.seek(0)
                    else:
                        time.sleep(0.1)
                    continue
                # Construct syslog message
                syslog_msg = create_syslog_message(line.strip(), config)
                # Send message
                if protocol == 'udp':
                    sock.sendto(syslog_msg.encode('utf-8'), (server_ip, server_port))
                else:
                    try:
                        sock.sendall(syslog_msg.encode('utf-8') + b'\\n')
                    except Exception as e:
                        print(f"TCP send error, reconnecting: {e}")
                        sock.close()
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((server_ip, server_port))
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
