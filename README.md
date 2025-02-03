### Usage Instructions

1. **Update the Config**: Modify `config.json` with your syslog server details.
    - `server_ip`: IP address of the syslog server.
    - `server_port`: Port (default: `514`).
    - `protocol`: `udp` or `tcp`.
    - `log_file`: Path to your log file (`logs.txt`).
    - `facility`: Syslog facility (default: `1` for user-level).
    - `severity`: Syslog severity (default: `6` for informational).
    - `app_name`: Application name included in syslog messages.
2. **Run the Forwarder**:
    
    ```bash
    python3 syslog_forwarder.py
    
    ```
    
3. **Test**:
    - Append logs to `logs.txt`:
        
        ```bash
        echo "Test log message" >> logs.txt
        
        ```
        
    - Verify logs appear on your syslog server.

### Notes

- **Syslog Format**: The script formats logs into RFC 5424-compliant messages.
- **File Rotation**: Handles basic file truncation (e.g., log rotation).
- **TCP Reconnection**: Attempts to reconnect if the TCP connection drops.
- **Security**: For production use, add encryption (TLS) and error handling.