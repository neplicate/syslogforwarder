# Syslog Forwarder

A lightweight, efficient tool for forwarding log entries from a file to a syslog server in real-time, following the RFC 5424 syslog protocol standard.

## Features

- **Real-time Log Forwarding**: Monitors log files and forwards new entries as they appear
- **Protocol Support**: Supports both UDP and TCP transport protocols
- **RFC 5424 Compliance**: Formats messages according to the syslog standard
- **File Rotation Handling**: Automatically detects and adapts to log file rotations/truncations
- **Connection Recovery**: Automatically attempts to reconnect if TCP connections are lost
- **Customizable Configuration**: Easy JSON-based configuration
- **Robust Error Handling**: Comprehensive logging and graceful error recovery
- **Command-line Options**: Support for custom config paths and verbose logging

## Installation

### Requirements

- Python 3.6 or higher
- No external dependencies beyond the Python standard library

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/neplicate/syslog-forwarder.git
   cd syslog-forwarder
   ```

2. Create or modify the configuration file (see Configuration section)

## Configuration

The forwarder uses a JSON configuration file (`config.json` by default) with the following parameters:

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `server_ip` | IP address of the syslog server | - | Yes |
| `server_port` | Port number of the syslog server | - | Yes |
| `log_file` | Path to the log file to monitor | - | Yes |
| `protocol` | Transport protocol (`udp` or `tcp`) | `udp` | No |
| `facility` | Syslog facility code (0-23) | `1` (user-level) | No |
| `severity` | Syslog severity code (0-7) | `6` (informational) | No |
| `app_name` | Application name for syslog messages | `syslog_forwarder` | No |
| `reconnect_delay` | Seconds to wait before reconnection attempts | `5` | No |
| `read_delay` | Seconds to wait between file reads when idle | `0.1` | No |

### Example Configuration

```json
{
    "server_ip": "10.0.0.1",
    "server_port": 514,
    "protocol": "tcp",
    "log_file": "/var/log/application.log",
    "facility": 1,
    "severity": 6,
    "app_name": "my_app",
    "reconnect_delay": 5,
    "read_delay": 0.1
}
```

## Usage

### Basic Usage

Run the forwarder with the default configuration file:

```bash
python syslogserver.py
```

### Advanced Usage

```bash
# Use a custom configuration file
python syslogserver.py --config /path/to/custom-config.json

# Enable verbose logging
python syslogserver.py --verbose

# Combine options
python syslogserver.py --config /path/to/custom-config.json --verbose
```

### Testing

1. Start the forwarder:
   ```bash
   python syslogserver.py
   ```

2. Add test messages to your log file:
   ```bash
   echo "Test log message" >> logs.txt
   ```

3. Verify that messages appear on your syslog server

## Syslog Format

Messages are formatted according to RFC 5424 with the following structure:

```
<PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID STRUCTURED-DATA MSG
```

Where:
- `PRI`: Priority value calculated as `facility*8 + severity`
- `VERSION`: Always 1 for RFC 5424
- `TIMESTAMP`: ISO8601 format with UTC timezone (e.g., `2025-02-28T12:34:56.789Z`)
- `HOSTNAME`: The hostname of the machine running the forwarder
- `APP-NAME`: The application name from configuration
- `PROCID`: The process ID of the forwarder
- `MSGID`: Not used (represented as `-`)
- `STRUCTURED-DATA`: Not used (represented as `-`)
- `MSG`: The log message content

## Production Considerations

For production deployments, consider the following:

### Security

- For sensitive logs, consider using TLS encryption for TCP connections
- Implement proper access controls on the log files and configuration
- Review and adjust syslog facility and severity levels according to your organization's policies

### Performance

- For high-volume logs, UDP may offer better performance but without delivery guarantees
- Adjust the `read_delay` parameter based on log volume and system resources
- Consider implementing batching for very high-volume environments

### Monitoring

- Implement external monitoring of the forwarder process
- Consider setting up alerts for connection failures or other critical errors

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Verify the syslog server IP and port
   - Check firewall rules between the forwarder and server
   - Verify the syslog server is running and accepting connections

2. **Messages Not Appearing**
   - Check that the syslog server is configured to accept the facility/severity level you're using
   - Verify the log file permissions allow the forwarder to read it
   - Enable verbose logging for more detailed output

3. **High CPU Usage**
   - Increase the `read_delay` parameter to reduce polling frequency
   - Check for very high log volume and consider optimizations

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to improve the functionality.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
