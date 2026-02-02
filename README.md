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
# Basic usage
python roboxtract.py -l domains.txt

# With output to file
python roboxtract.py -l domains.txt -o endpoints.txt

# With threading
python roboxtract.py -l domains.txt --threads 10

# Verbose mode
python roboxtract.py -l domains.txt -v
```

## Input Format

Simple list of domains (one per line):
```
https://example.com
https://api.example.com
https://admin.example.com
```

## License

MIT License - see [LICENSE](LICENSE) for details.