# PancakePounder

PancakePounder is a Python-based, multi-threaded login brute-force utility designed for testing web applications that use CSRF-protected login forms. It can automate credential testing against a target login endpoint, extract CSRF tokens dynamically, and validate successful logins using either HTTP status codes or custom regex matching.

This project is intended for authorized security testing and educational use only. Do not use it against systems you do not own or have explicit permission to test.

## Features

- Multi-threaded credential attacks for faster testing
- Supports a single username/password or full wordlists
- Extracts CSRF tokens from the target page or a separate CSRF endpoint
- Customizes POST body parameters with placeholders such as `*USER*` and `*PASS*`
- Allows custom query strings and request data
- Matches on HTTP status codes or response content regex
- Saves successful results to an output file when requested
- Supports SSL verification toggling for misconfigured or test environments

## Requirements

- Python 3.x
- `requests`

Install the dependency:

```bash
pip install requests
```

## Usage

```bash
python3 PancakePounder.py --help
```

### Example: standard login attack with CSRF token regex

```bash
python3 PancakePounder.py \
  --host "https://example.com/login" \
  --data "username=*USER*&password=*PASS*" \
  -U users.txt \
  -P passwords.txt \
  --csrf-regex "csrf_token[^>]*value=\"([^\"]+)\"" \
  --csrf-param "csrf_token" \
  -ms "200-299,301,302"
```

### Example: using a separate CSRF URL

```bash
python3 PancakePounder.py \
  --host "https://example.com/login" \
  --data "username=*USER*&password=*PASS*" \
  -U users.txt \
  -P passwords.txt \
  --csrf-url "https://example.com/login" \
  --csrf-regex "csrf_token[^>]*value=\"([^\"]+)\"" \
  --csrf-param "csrf_token" \
  -mr "login_success" \
  -ms "200-299,301,302"
```

## Arguments

- `--host`: Target login URL
- `-U, --users`: Path to a usernames wordlist
- `-u, --user`: Single username to test
- `-P, --passwords`: Path to a passwords wordlist
- `-p, --password`: Single password to test
- `-cr, --csrf-regex`: Regex used to extract the CSRF token
- `-cp, --csrf-param`: CSRF parameter name to submit in the login request
- `-cu, --csrf-url`: Optional URL used to fetch CSRF data
- `-mr, --match-regex`: Regex to validate a successful login response
- `-ms, --match-status`: Accepted HTTP status codes for success matching
- `-d, --data`: Request body template containing `*USER*` and `*PASS*`
- `-q, --query`: Query parameters for GET requests
- `-t, --threads`: Number of concurrent threads (default: `5`)
- `-o, --output`: File to store successful result output
- `-vr, --verify`: Disable SSL certificate verification
- `--verbose`: Enable verbose output

## Important Notes

- `--data` must include the placeholders `*USER*` and `*PASS*` for credential substitution.
- If you use `--match-status` and `--match-regex`, the script checks either or both depending on which options are supplied.
- The program is designed for legitimate assessment and testing workflows. Use responsibly and only on systems you are authorized to evaluate.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Project Structure

```text
PancakePounder/
├── PancakePounder.py
├── README.md
├── LICENSE
└── (optional wordlists / output files)
```

## Disclaimer

This tool can be abused for unauthorized attacks. The author and maintainers are not responsible for misuse. Use only in environments where you have explicit permission to perform security testing.
