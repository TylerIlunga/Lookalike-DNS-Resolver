"""
Locust setup for load testing one-shot echo server
"""
import socket
import time
from random import randint
from os import environ
from dotenv import load_dotenv

from locust import Locust, TaskSet, events, task, between

load_dotenv()

LOCUST_HOST = environ['LOCUST_HOST']
SERVER_PORT = environ['SERVER_PORT']


class ClientBehavior(TaskSet):
    @task
    def bing_domain_query_input(self):
        start_time = time.time()
        response = ''
        try:
            query = '2dd1012000010000000000010462696e6703636f6d00000100010000291000000000000000'
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect((self.locust.host, int(SERVER_PORT)))
                sock.sendall(bytearray.fromhex(query))
                response = sock.recv(4096)
        except Exception as e:
            total_time = int(time.time() - start_time) * 1000
            events.request_failure.fire(request_type='input',
                                        name='bing_domain_query_input',
                                        response_time=total_time,
                                        response_length=0,
                                        exception=e)
        else:
            total_time = int(time.time() - start_time) * 1000
            events.request_success.fire(request_type='input',
                                        name='bing_domain_query_input',
                                        response_time=total_time,
                                        response_length=len(response))
    @task
    def facebook_domain_query_input(self):
        start_time = time.time()
        response = ''
        try:
            query = 'b121012000010000000000010866616365626f6f6b03636f6d00000100010000291000000000000000'
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect((self.locust.host, int(SERVER_PORT)))
                sock.sendall(bytearray.fromhex(query))
                response = sock.recv(4096)
        except Exception as e:
            total_time = int(time.time() - start_time) * 1000
            events.request_failure.fire(request_type='input',
                                        name='facebook_domain_query_input',
                                        response_time=total_time,
                                        response_length=0,
                                        exception=e)
        else:
            total_time = int(time.time() - start_time) * 1000
            events.request_success.fire(request_type='input',
                                        name='facebook_domain_query_input',
                                        response_time=total_time,
                                        response_length=len(response))
    @task
    def uber_domain_query_input(self):
        start_time = time.time()
        response = ''
        try:
            query = 'a38301200001000000000001047562657203636f6d00000100010000291000000000000000'
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect((self.locust.host, int(SERVER_PORT)))
                sock.sendall(bytearray.fromhex(query))
                response = sock.recv(4096)
        except Exception as e:
            total_time = int(time.time() - start_time) * 1000
            events.request_failure.fire(request_type='input',
                                        name='uber_domain_query_input',
                                        response_time=total_time,
                                        response_length=0,
                                        exception=e)
        else:
            total_time = int(time.time() - start_time) * 1000
            events.request_success.fire(request_type='input',
                                        name='uber_domain_query_input',
                                        response_time=total_time,
                                        response_length=len(response))

    @task
    def invalid_domain_query_input(self):
        start_time = time.time()
        response = ''
        try:
            query = '72616e646f6d' # "random"
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect((self.locust.host, int(SERVER_PORT)))
                sock.sendall(bytearray.fromhex(query))
                response = sock.recv(4096)
        except Exception as e:
            total_time = int(time.time() - start_time) * 1000
            events.request_failure.fire(request_type='input',
                                        name='no_domain_query_input',
                                        response_time=total_time,
                                        response_length=0,
                                        exception=e)
        else:
            total_time = int(time.time() - start_time) * 1000
            events.request_success.fire(request_type='input',
                                        name='no_domain_query_input',
                                        response_time=total_time,
                                        response_length=len(response))


class SocketUser(Locust):
    host = LOCUST_HOST
    task_set = ClientBehavior
    wait_time = between(1, 2)
