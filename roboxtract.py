#!/usr/bin/env python3

import requests
import argparse
import urllib3
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ANSI Color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def disable():
        Colors.HEADER = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.RED = ''
        Colors.ENDC = ''
        Colors.BOLD = ''

def print_banner():
    """Print tool banner"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
██████╗  ██████╗ ██████╗  ██████╗ ██╗  ██╗████████╗██████╗  █████╗  ██████╗████████╗
██╔══██╗██╔═══██╗██╔══██╗██╔═══██╗╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝
██████╔╝██║   ██║██████╔╝██║   ██║ ╚███╔╝    ██║   ██████╔╝███████║██║        ██║   
██╔══██╗██║   ██║██╔══██╗██║   ██║ ██╔██╗    ██║   ██╔══██╗██╔══██║██║        ██║   
██║  ██║╚██████╔╝██████╔╝╚██████╔╝██╔╝ ██╗   ██║   ██║  ██║██║  ██║╚██████╗   ██║   
╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝   ╚═╝   
                                                                                                                                                                                                                                                                                                                                                                      
{Colors.ENDC}{Colors.CYAN}
    Extract forbidden endpoints from robots.txt
    Version 1.0 | @NeoPrime
{Colors.ENDC}"""
    print(banner)

def parse_robots_txt(content, base_url):
    """Extract disallowed paths from robots.txt content"""
    endpoints = set()
    
    if not content:
        return endpoints
    
    # Convert bytes to string if needed
    if isinstance(content, bytes):
        content = content.decode('utf-8', errors='ignore')
    
    # Clean base URL (remove /robots.txt)
    base_domain = base_url.replace('/robots.txt', '').rstrip('/')
    
    for line in content.split('\n'):
        line = line.strip()
        
        # Look for Disallow lines
        if line.lower().startswith('disallow:'):
            try:
                path = line.split(':', 1)[1].strip()
            except IndexError:
                continue
            
            # Skip empty, root-only, or wildcards
            if not path or path == '/' or '*' in path:
                continue
            
            # Remove comments
            for delimiter in ['#', '\t']:
                if delimiter in path:
                    path = path.split(delimiter)[0].strip()
            
            if path:
                full_url = base_domain + path
                endpoints.add(full_url)
    
    return endpoints

def request(subdomain, args):
    """Fetch robots.txt from subdomain"""
    # Build robots.txt URL
    if not subdomain.endswith('/robots.txt'):
        if subdomain.endswith('/'):
            url = subdomain + 'robots.txt'
        else:
            url = subdomain + '/robots.txt'
    else:
        url = subdomain
    
    try:
        # Build headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        if args.header:
            for header in args.header:
                if ':' in header:
                    key, value = header.split(':', 1)
                    headers[key.strip()] = value.strip()
        
        # Make request
        response = requests.get(
            url=url,
            headers=headers,
            timeout=20,
            verify=False,
            allow_redirects=False
        )
        
        return response
    
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None

def main():
    # Configure Parser
    parser = argparse.ArgumentParser(
        prog='RoboXtract',
        description='Extract hidden endpoints from robots.txt files',
        epilog='Example: python roboxtract.py -l domains.txt -o endpoints.txt -t 20 -v',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Configure Arguments
    parser.add_argument(
        '-l', '--list',
        required=True,
        metavar='FILE',
        help='file containing list of domains (one per line)'
    )
    parser.add_argument(
        '-o', '--output',
        metavar='FILE',
        help='output file for extracted endpoints'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='enable verbose output'
    )
    parser.add_argument(
        '-t', '--threads',
        type=int,
        default=10,
        metavar='N',
        help='number of concurrent threads (default: 10)'
    )
    parser.add_argument(
        '-H', '--header',
        action='append',
        metavar='HEADER',
        help='custom header (format: "Key: Value")'
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='disable colored output'
    )

    # Parse Arguments
    args = parser.parse_args()
    
    # Disable colors if requested or not a TTY
    if args.no_color or not sys.stdout.isatty():
        Colors.disable()
    
    # Print banner
    print_banner()
    
    # Load domains
    print(f"{Colors.BLUE}[*]{Colors.ENDC} Loading domains from {Colors.BOLD}{args.list}{Colors.ENDC}")
    
    subdomains = set()
    try:
        with open(args.list, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    subdomains.add(line)
    except FileNotFoundError:
        print(f"{Colors.RED}[✗]{Colors.ENDC} File not found: {args.list}")
        return 1
    except Exception as e:
        print(f"{Colors.RED}[✗]{Colors.ENDC} Error loading file: {e}")
        return 1
    
    if not subdomains:
        print(f"{Colors.RED}[✗]{Colors.ENDC} No domains found in file")
        return 1
    
    print(f"{Colors.GREEN}[✓]{Colors.ENDC} Loaded {Colors.BOLD}{len(subdomains)}{Colors.ENDC} unique domains")
    print(f"{Colors.BLUE}[*]{Colors.ENDC} Using {Colors.BOLD}{args.threads}{Colors.ENDC} concurrent threads")
    
    # Threading
    results = []
    
    print(f"\n{Colors.BLUE}[*]{Colors.ENDC} Fetching robots.txt files...")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.ENDC}")
    
    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_domain = {
                executor.submit(request, subdomain, args): subdomain
                for subdomain in subdomains
            }
            
            completed = 0
            total = len(future_to_domain)
            found_count = 0
            
            try:
                for future in as_completed(future_to_domain):
                    completed += 1
                    subdomain = future_to_domain[future]
                    
                    try:
                        result = future.result()
                        
                        if result and result.status_code == 200:
                            results.append(result)
                            found_count += 1
                            
                            if args.verbose:
                                # Clear progress line, print message
                                print(f"\r{' ' * 120}\r{Colors.GREEN}[✓]{Colors.ENDC} {result.url}")
                    
                    except Exception:
                        pass
                    
                    # Progress bar (always shown)
                    percentage = (completed / total) * 100
                    bar_length = 50
                    filled = int(bar_length * completed / total)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    
                    # Print progress
                    print(f"\r{Colors.CYAN}[{bar}]{Colors.ENDC} {completed}/{total} ({percentage:.0f}%) | Found: {Colors.GREEN}{found_count}{Colors.ENDC}  ", end='', flush=True)
                
            except KeyboardInterrupt:
                # Clear progress line
                print(f"\r{' ' * 120}\r", end='')
                print(f"\n{Colors.YELLOW}[!]{Colors.ENDC} Interrupted by user")
                print(f"{Colors.BLUE}[*]{Colors.ENDC} Processed {completed}/{total} domains")
                
                # Cancel remaining futures
                for f in future_to_domain.keys():
                    f.cancel()
                
                # Force exit
                os._exit(130)
            
            print()  # New line after completion
    
    except KeyboardInterrupt:
        os._exit(130)
    
    print(f"{Colors.CYAN}{'─' * 60}{Colors.ENDC}")
    print(f"{Colors.GREEN}[✓]{Colors.ENDC} Found {Colors.BOLD}{len(results)}{Colors.ENDC} accessible robots.txt files")
    
    # Extract endpoints
    if not results:
        print(f"{Colors.YELLOW}[!]{Colors.ENDC} No robots.txt files found")
        return 0
    
    print(f"\n{Colors.BLUE}[*]{Colors.ENDC} Extracting disallowed endpoints...")
    
    total_urls = set()
    for result in results:
        if result.content:
            endpoints = parse_robots_txt(result.content, result.url)
            total_urls.update(endpoints)
            
            if args.verbose and endpoints:
                print(f"{Colors.GREEN}[+]{Colors.ENDC} {result.url} → {len(endpoints)} endpoints")
    
    print(f"{Colors.GREEN}[✓]{Colors.ENDC} Extracted {Colors.BOLD}{len(total_urls)}{Colors.ENDC} unique endpoints")
    
    # Save results
    if args.output:
        print(f"\n{Colors.BLUE}[*]{Colors.ENDC} Saving results to {Colors.BOLD}{args.output}{Colors.ENDC}")
        
        try:
            output_dir = os.path.dirname(args.output)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            with open(args.output, "w", encoding='utf-8') as f:
                for url in sorted(total_urls):
                    f.write(url + '\n')
            
            print(f"{Colors.GREEN}[✓]{Colors.ENDC} Successfully saved {len(total_urls)} endpoints")
            
        except PermissionError:
            print(f"{Colors.RED}[✗]{Colors.ENDC} Permission denied: {args.output}")
            return 1
        except Exception as e:
            print(f"{Colors.RED}[✗]{Colors.ENDC} Error writing file: {e}")
            return 1
    else:
        # Print to stdout
        print(f"\n{Colors.CYAN}{'─' * 60}{Colors.ENDC}")
        print(f"{Colors.BOLD}Extracted Endpoints:{Colors.ENDC}\n")
        for url in sorted(total_urls):
            print(f"{Colors.ENDC}{url}")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}[✓] Done!{Colors.ENDC}")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        os._exit(130)