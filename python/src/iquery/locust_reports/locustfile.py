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
    def bing_ip_query_input(self):
        start_time = time.time()
        response = ''
        try:
            query = '55750120000100000000000103313732033231370231310331373400000100010000291000000000000000'
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect((self.locust.host, int(SERVER_PORT)))
                sock.sendall(bytearray.fromhex(query))
                response = sock.recv(4096)
        except Exception as e:
            total_time = int(time.time() - start_time) * 1000
            events.request_failure.fire(request_type='input',
                                        name='bing_ip_query_input',
                                        response_time=total_time,
                                        response_length=0,
                                        exception=e)
        else:
            total_time = int(time.time() - start_time) * 1000
            events.request_success.fire(request_type='input',
                                        name='bing_ip_query_input',
                                        response_time=total_time,
                                        response_length=len(response))
    @task
    def facebook_ip_query_input(self):
        start_time = time.time()
        response = ''
        try:
            query = 'b3a5012000010000000000010331353103313031033132390331343000000100010000291000000000000000'
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect((self.locust.host, int(SERVER_PORT)))
                sock.sendall(bytearray.fromhex(query))
                response = sock.recv(4096)
        except Exception as e:
            total_time = int(time.time() - start_time) * 1000
            events.request_failure.fire(request_type='input',
                                        name='facebook_ip_query_input',
                                        response_time=total_time,
                                        response_length=0,
                                        exception=e)
        else:
            total_time = int(time.time() - start_time) * 1000
            events.request_success.fire(request_type='input',
                                        name='facebook_ip_query_input',
                                        response_time=total_time,
                                        response_length=len(response))
    @task
    def uber_ip_query_input(self):
        start_time = time.time()
        response = ''
        try:
            query = '3ed201200001000000000001023133023333033232390331323900000100010000291000000000000000'
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect((self.locust.host, int(SERVER_PORT)))
                sock.sendall(bytearray.fromhex(query))
                response = sock.recv(4096)
        except Exception as e:
            total_time = int(time.time() - start_time) * 1000
            events.request_failure.fire(request_type='input',
                                        name='uber_ip_query_input',
                                        response_time=total_time,
                                        response_length=0,
                                        exception=e)
        else:
            total_time = int(time.time() - start_time) * 1000
            events.request_success.fire(request_type='input',
                                        name='uber_ip_query_input',
                                        response_time=total_time,
                                        response_length=len(response))

    @task
    def invalid_ip_query_input(self):
        start_time = time.time()
        response = '' 
        try:
            query = '302e302e302e30' # 0.0.0.0
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect((self.locust.host, int(SERVER_PORT)))
                sock.sendall(bytearray.fromhex(query))
                response = sock.recv(4096)
        except Exception as e:
            total_time = int(time.time() - start_time) * 1000
            events.request_failure.fire(request_type='input',
                                        name='no_ip_query_input',
                                        response_time=total_time,
                                        response_length=0,
                                        exception=e)
        else:
            total_time = int(time.time() - start_time) * 1000
            events.request_success.fire(request_type='input',
                                        name='no_ip_query_input',
                                        response_time=total_time,
                                        response_length=len(response))



class SocketUser(Locust):
    host = LOCUST_HOST
    task_set = ClientBehavior
    wait_time = between(1, 2)
