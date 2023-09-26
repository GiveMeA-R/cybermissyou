import os
import re
import subprocess
import xml.etree.ElementTree as ET
import requests
from bruteforce import BruteForcer, try_ftp_login, try_smb_login, try_ssh_login, try_mongodb_login
from exportDocx import generate_docx_from_log

def download_passwords(url):
    response = requests.get(url)
    return response.text.splitlines()

def parse_nmap_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for host in root.findall('host'):
        ip = host.find('address').get('addr')
        for port in host.iter('port'):
            yield ip, int(port.get('portid')), port.find('service').get('name')

def append_to_file(path, text):
    with open(path, 'a') as file:
        file.write(text)

def scan_networks(networks, output_folder, password_list_url):
    passwords = download_passwords(password_list_url)
    usernames = ["root", "admin", "administrator", "guest", "test", "user"]
    discovered_services = set()
    brute_forcer = BruteForcer(usernames, passwords)
    successful_logins = []  # New variable to store successful logins
    for network in networks:
        print(f"Scanning network: {network}")
        xml_file = f"{output_folder}/{network.replace('/', '_')}_nmap.xml"
        subprocess.run(["nmap", "-p445,3389,20,21,22,23,5986,5985,9092,27017,27018,27019,11211,9200,5601,53,69,161,389,135,139,2049,2301,2381,5000,5900,5800,6000,9100,80,443,88", "-Pn", "-sV", "-sS", "-O", "-T3", "-oX", xml_file, network])

        for host, port, service in parse_nmap_xml(xml_file):
            with open(f"{output_folder}/{network.replace('/', '_')}_results.txt", "a") as file:
                file.write(f"Discovered {service} on {host}:{port}\n")
            discovered_services.add((host, service, port))

    print("Scanning process finished. Results are saved in separate files.")
    print("The following services were discovered and could be subject to a brute-force attack:")

    for host, service, port in discovered_services:
        if service in ['ftp', 'ssh', 'microsoft-ds' 'microsoft-ds?', 'mongod']:
            print(f"Host: {host}, Service: {service}, Port: {port}")

    while True:
        brute_force_input = input("Do you want to bruteforce? (Yes/No): ")
        if brute_force_input.lower() == "no":
            print("Switching to main menu...")
            break
        elif brute_force_input.lower() == "yes":
            while True:
                choice = input(
                    "Choose an option:\n"
                    "1. Brute-force specific host:port pairs\n"
                    "2. Brute-force all excluding specific services or host:port pairs\n"
                    "3. Brute-force all\n"
                    "4. Brute-force all character combinations\n"
                    "Choice: "
                )
                try:
                    if choice == "1":
                        brute_force_target = input("Input targets for bruteforce (format IP:port), separate by comma: ")
                        targets = [tuple(target.strip().split(":")) for target in brute_force_target.split(",")]
                        targets = [(host, int(port)) for host, port in targets]  # convert port to integer
                        targets = [target for target in targets if target in [(h, p) for h, s, p in discovered_services]]  # only keep valid targets
                    elif choice == "2":
                        exclusion_target = input("Input targets (format IP:port) or serivce (port of serivce) for exclusion, separate by comma: ")
                        exclusions = exclusion_target.split(",")
                        exclusions = [int(exclusion.strip()) if ":" not in exclusion else tuple(exclusion.strip().split(":")) for exclusion in exclusions]
                        targets = [(host, port) for host, service, port in discovered_services if service in ['ftp', 'ssh', 'microsoft-ds', 'microsoft-ds?', 'mongod'] and (host, port) not in exclusions and port not in exclusions]
                    elif choice == "3":
                        targets = [(host, port) for host, service, port in discovered_services if service in ['ftp', 'ssh', 'microsoft-ds', 'microsoft-ds?', 'mongod']]
                    elif choice == "4":
                        targets = [(host, port) for host, service, port in discovered_services if service in ['ftp', 'ssh', 'microsoft-ds', 'microsoft-ds?', 'mongod']]
                        for target in targets:
                            result = brute_forcer.bruteforce_target_character(target, f"{output_folder}/{network.replace('/', '_')}_results.txt")
                            successful_logins += result  # Add the returned successful logins to the list
                    else:
                        print("Invalid choice. Please try again.")
                        continue

                    for target in targets:
                        result = brute_forcer.bruteforce_target(target, f"{output_folder}/{network.replace('/', '_')}_results.txt")
                        successful_logins += result  # Add the returned successful logins to the list

                    continue_bruteforcing = input("Do you want to bruteforce another target? (Yes/No): ")
                    if continue_bruteforcing.lower() != "yes":
                        print("Switching to main menu...")
                        break  # Break out of the inner loop
                except ValueError:
                    print("Invalid input format. Please enter in format IP:port where port is a number.")
            break
        else:
            print("Invalid input. Please try again.")
            
    return f"{output_folder}/{network.replace('/', '_')}_results.txt", successful_logins, discovered_services

    # for file_name in os.listdir(output_folder):
    #     if file_name.endswith("nmap.xml"):
    #         os.remove(os.path.join(output_folder, file_name))
 

def start_scan():
    subnet_regex = r"\b((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/(3[0-2]|[12]?[0-9])\b"
    while True:
        network_input = input("Input networks for scan (format x.x.x.x/y), separate by comma: ")
        networks = [net.strip() for net in network_input.split(",")]
        if "0.0.0.0/0" in networks:
            print("The subnet 0.0.0.0/0 is not allowed. Please try again.")
        elif all(re.match(subnet_regex, net) for net in networks):
            break
        else:
            print("Invalid subnet format. Please try again.")

    output_folder = "scan_results"
    password_list_url = "https://raw.githubusercontent.com/richiemann/vietnam-password-lists/master/top1million-vn-passwords.txt"
    log_filename, successful_logins, discovered_services = scan_networks(networks, output_folder, password_list_url)
    return log_filename, successful_logins, discovered_services
    
   