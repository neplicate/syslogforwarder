import json
import socket
import os
import time
import logging
from datetime import datetime
import argparse
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('syslog_forwarder')

def load_config(config_path):
    """Load and validate configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Validate required keys
        required_keys = ['server_ip', 'server_port', 'log_file']
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ValueError(f"Missing required config keys: {', '.join(missing_keys)}")
        
        # Set defaults for optional keys
        config.setdefault('protocol', 'udp')
        config.setdefault('facility', 1)
        config.setdefault('severity', 6)
        config.setdefault('app_name', 'syslog_forwarder')
        config.setdefault('reconnect_delay', 5)
        config.setdefault('read_delay', 0.1)
        
        return config
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        sys.exit(1)

def create_syslog_message(log_line, config):
    """Create an RFC 5424 compliant syslog message."""
    pri = config['facility'] * 8 + config['severity']
    version = 1
    timestamp = datetime.utcnow().isoformat() + 'Z'
    hostname = socket.gethostname()
    app_name = config['app_name']
    pid = os.getpid()
    return f"<{pri}>{version} {timestamp} {hostname} {app_name} {pid} - - {log_line}"

def create_socket(config):
    """Create and configure a socket based on the protocol."""
    protocol = config['protocol'].lower()
    server_ip = config['server_ip']
    server_port = config['server_port']
    
    if protocol == 'udp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.info(f"Created UDP socket to {server_ip}:{server_port}")
        return sock
    elif protocol == 'tcp':
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((server_ip, server_port))
            logger.info(f"Connected to TCP server at {server_ip}:{server_port}")
            return sock
        except Exception as e:
            logger.error(f"TCP connection error: {e}")
            return None
    else:
        raise ValueError("Invalid protocol. Use 'udp' or 'tcp'.")

def send_message(sock, message, config):
    """Send a message using the configured protocol."""
    server_ip = config['server_ip']
    server_port = config['server_port']
    protocol = config['protocol'].lower()
    
    try:
        if protocol == 'udp':
            sock.sendto(message.encode('utf-8'), (server_ip, server_port))
            return True
        else:  # TCP
            sock.sendall(message.encode('utf-8') + b'\n')
            return True
    except Exception as e:
        logger.error(f"Send error: {e}")
        return False

def monitor_file(config, sock):
    """Monitor a log file and forward new entries to the syslog server."""
    log_file = config['log_file']
    read_delay = config['read_delay']
    reconnect_delay = config['reconnect_delay']
    protocol = config['protocol'].lower()
    
    try:
        # Ensure the log file exists
        open(log_file, 'a').close()
        
        with open(log_file, 'r') as f:
            # Move to the end of the file
            f.seek(0, os.SEEK_END)
            logger.info(f"Monitoring {log_file} for new entries...")
            
            while True:
                current_pos = f.tell()
                line = f.readline()
                
                if not line:
                    # Check if file was truncated (e.g., log rotation)
                    if os.path.getsize(log_file) < current_pos:
                        logger.info("Log file was truncated, resetting position")
                        f.seek(0)
                    else:
                        time.sleep(read_delay)
                    continue
                
                # Construct and send syslog message
                syslog_msg = create_syslog_message(line.strip(), config)
                
                if not send_message(sock, syslog_msg, config):
                    if protocol == 'tcp':
                        logger.info(f"Attempting to reconnect in {reconnect_delay} seconds...")
                        time.sleep(reconnect_delay)
                        new_sock = create_socket(config)
                        if new_sock:
                            sock = new_sock
                        else:
                            continue
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, exiting...")
    except Exception as e:
        logger.error(f"Error monitoring file: {e}")
    finally:
        return sock

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Syslog Forwarder')
    parser.add_argument('-c', '--config', default='config.json',
                        help='Path to config file (default: config.json)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging')
    return parser.parse_args()

def main():
    """Main function to run the syslog forwarder."""
    args = parse_arguments()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Load configuration
        config = load_config(args.config)
        logger.info(f"Configuration loaded from {args.config}")
        
        # Create socket
        sock = create_socket(config)
        if not sock:
            logger.error("Failed to create socket, exiting")
            return
        
        # Monitor log file and forward entries
        sock = monitor_file(config, sock)
        
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
    finally:
        if 'sock' in locals() and sock:
            sock.close()
            logger.info("Socket closed")

if __name__ == "__main__":
    main()
