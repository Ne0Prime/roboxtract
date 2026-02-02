# RoboXtract

RoboXtract automates the discovery of hidden endpoints by parsing robots.txt files across multiple domains. Feed it a list of targets and get back every disallowed path as a ready-to-test URL.

## Features

- Fast concurrent processing
- Extracts all disallowed paths from robots.txt
- Automatically combines base URLs with paths
- Outputs clean, testable endpoint lists

## Installation
```bash
git clone https://github.com/Ne0Prime/roboxtract.git
cd roboxtract
pip install -r requirements.txt
```

## Usage
```bash
# Basic scan
python roboxtract.py -l domains.txt -o endpoints.txt

# Fast scan (20 threads)
python roboxtract.py -l domains.txt -o endpoints.txt -t 20

# Verbose mode
python roboxtract.py -l domains.txt -v

# Custom headers
python roboxtract.py -l domains.txt -H "User-Agent: Custom"
```

### Options
```
-l, --list      Input file with domains (required)
-o, --output    Output file for endpoints
-t, --threads   Number of threads (default: 10)
-v, --verbose   Enable verbose output
-H, --header    Custom HTTP header
--no-color      Disable colored output
```

## Input Format

Simple list of domains (one per line):
```
https://example.com
https://api.example.com
https://admin.example.com
```

## Requirements

- Python 3.7+
- requests
- urllib3

## License

MIT License - see [LICENSE](LICENSE) for details.