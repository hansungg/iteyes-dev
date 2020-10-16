#!/usr/bin/env python
# coding: utf-8
import sys
import os
import hashlib
import hmac
import base64
import requests
import time
import urllib

import xml.etree.ElementTree as elemTree


# answer key
ACCESS_KEY = "test1"
SECRET_KEY = "test2"

SECRET_KEY_ENCODE = bytes(SECRET_KEY, 'UTF-8')
NCP_URL = "https://ncloud.apigw.ntruss.com"

server_uri = "/server/v2/"

def get_timestamp():
    timestamp = int(time.time() * 1000)
    timestamp = str(timestamp)
    return timestamp

def set_key(access, secret):
    ACCESS_KEY=access
    SECRET_KEY_ENCODE=bytes(secret, 'UTF-8')
    
def make_signature(uri):
    method = "GET"
    message = method + " " + uri + "\n" + get_timestamp() + "\n"+ ACCESS_KEY
    message = bytes(message, 'UTF-8')
    signingKey = base64.b64encode(hmac.new(SECRET_KEY_ENCODE, message, digestmod=hashlib.sha256).digest())
    return signingKey

def make_post_signature(uri):
    method = "POST"
    message = method + " " + uri + "\n" + get_timestamp() + "\n"+ ACCESS_KEY
    message = bytes(message, 'UTF-8')
    signingKey = base64.b64encode(hmac.new(SECRET_KEY_ENCODE, message, digestmod=hashlib.sha256).digest())
    return signingKey

def send_get_uri(uri):
    signature = make_signature(uri)
    headers = {'x-ncp-apigw-timestamp': get_timestamp(), 
               'x-ncp-iam-access-key': ACCESS_KEY, 
               'x-ncp-apigw-signature-v1': signature}
    response = requests.get(NCP_URL + uri, headers=headers)
    return response

def send_get_uri_with_param(uri,params):
    signature = make_signature(uri + "?" + urllib.parse.urlencode(params))
    headers = {'x-ncp-apigw-timestamp': get_timestamp(), 
               'x-ncp-iam-access-key': ACCESS_KEY, 
               'x-ncp-apigw-signature-v1': signature}
    response = requests.get(NCP_URL + uri, params=params, headers=headers)
    return response

def send_post_uri(uri):
    signature = make_signature(uri)
    headers = {'x-ncp-apigw-timestamp': get_timestamp(), 
               'x-ncp-iam-access-key': ACCESS_KEY, 
               'x-ncp-apigw-signature-v1': signature}
    response = requests.post(NCP_URL + uri, headers=headers)
    return response

def check_xml_parserable(raw_text):
    try:
        tree = elemTree.fromstring(raw_text)
        print('XML well formed, syntax ok.')
        return tree;
    except IOError:
        print('Invalid File')
        return None;
    except:
        print('Unknown error, exiting.')
        return None;
    
def check_error_response(raw_text):
    print("error")
    if check_xml_parserable(raw_text) is None:
        return "0";
    return_message = tree.find("returnMessage").text
    return_code = tree.find("returnCode").text
    print(return_code)
    print(return_message)
    return return_code;

# Server List Req
def get_server_list():
    uri = server_uri + "getServerInstanceList"
    res = send_get_uri(uri)
    if res.status_code > 399 :
        return check_error_response(res.text);
    tree = elemTree.fromstring(res.text)
    #print(res.text)
    if( tree.find("totalRows").text == "0" ):
        print("there are no Server")
    server_list = tree.findall("serverInstanceList/serverInstance")
    for server in server_list:
        print (server.find("serverInstanceNo").text + " | "
               + server.find("serverName").text + " | "
               + server.find("privateIp").text + " | "
               + server.find("serverImageName").text + " | "
               + server.findtext("serverInstanceStatus/codeName") + " ")
    return server_list;

# Get Server Status Req
def get_server(serverInstanceNo):
    uri = server_uri + "getServerInstanceList" + "?serverInstanceNoList.1=" + serverInstanceNo
    res = send_get_uri(uri)
    if res.status_code > 399 :
        return check_error_response(res.text);
    tree = elemTree.fromstring(res.text)
    #print(res.text)
    if( tree.find("totalRows").text == "0" ):
        print("there are no Server")
        return None;
    server_object = tree.findall("serverInstanceList/serverInstance")
    for server in server_object:
        print (server.find("serverInstanceNo").text + " | "
               + server.find("serverName").text + " | "
               + server.find("privateIp").text + " | "
               + server.find("serverImageName").text + " | "
               + server.findtext("serverInstanceStatus/codeName") + " | "
               + server.findtext("serverInstanceStatus/code") + " ")
    server_status = server.findtext("serverInstanceStatus/code")
    return server_status;

# Get Server Operation Req
def get_server_op(serverInstanceNo):
    uri = server_uri + "getServerInstanceList" + "?serverInstanceNoList.1=" + serverInstanceNo
    res = send_get_uri(uri)
    if res.status_code > 399 :
        return check_error_response(res.text);
    tree = elemTree.fromstring(res.text)
    #print(res.text)
    if( tree.find("totalRows").text == "0" ):
        print("there are no Server")
        return None;
    server_object = tree.findall("serverInstanceList/serverInstance")
    for server in server_object:
        print (server.find("serverInstanceNo").text + " | "
               + server.find("serverName").text + " | "
               + server.find("privateIp").text + " | "
               + server.find("serverImageName").text + " | "
               + server.findtext("serverInstanceOperation/codeName") + " | "
               + server.findtext("serverInstanceOperation/code") + " ")
    server_op_status = server.findtext("serverInstanceOperation/code")
    return server_op_status;

# Server Stop Req
def stop_server_by_id(server_id):
    uri = server_uri + "stopServerInstances" + "?serverInstanceNoList.1=" + server_id
    res = send_get_uri(uri)
    if res.status_code > 399 :
        return check_error_response(res.text);
    tree = elemTree.fromstring(res.text)
    return_message = tree.find("returnMessage").text
    return_code = tree.find("returnCode").text
    print(return_code)
    print(return_message)
    return return_code;

# Make Server Image (when server stoped)
def create_server_image_by_id(server_id):
    uri = server_uri + "createMemberServerImage" + "?serverInstanceNo=" + server_id
    res = send_get_uri(uri)
    if res.status_code > 400 :
        return check_error_response(res.text);
    tree = elemTree.fromstring(res.text)
    return_message = tree.find("returnMessage").text
    return_code = tree.find("returnCode").text
    print(return_code)
    print(return_message)
    return return_code;

# Server Start Req
def start_server_by_id(server_id):
    uri = server_uri + "startServerInstances" + "?serverInstanceNoList.1=" + server_id
    res = send_get_uri(uri)
    if res.status_code > 400 :
        return check_error_response(res.text);
    tree = elemTree.fromstring(res.text)
    return_message = tree.find("returnMessage").text
    return_code = tree.find("returnCode").text
    print(return_code)
    print(return_message)
    return return_code

def get_server_image_list():
    uri = server_uri + "getMemberServerImageList"
    res = send_get_uri(uri)
    if res.status_code > 400 :
        return check_error_response(res.text);
    tree = elemTree.fromstring(res.text)
    #print(res.text)
    if( tree.find("totalRows").text == "0" ):
        print("there are no Server")
    server_object = tree.findall("memberServerImageList/memberServerImage")
    for server in server_object:
        print (server.find("memberServerImageNo").text + " | "
               + server.find("memberServerImageName").text + " | "
               + server.find("originalServerInstanceNo").text + " | "
               + server.find("originalServerName").text + " | "
               + server.findtext("createDate") )
    return tree;

def get_server_image_by_id(server_id):
    server_object = get_server_image_list()
    server_object = server_object.findall("memberServerImageList/memberServerImage")
    image_no_list = []
    print(server_object)
    for server in server_object:
        server_no = server.find("originalServerInstanceNo").text
        if(server_no == server_id):
            image_no = server.find("memberServerImageNo").text
            print("match image found! " + image_no)
            image_no_list.append(image_no)
    return image_no_list;

# Make Server Image (when server stoped)
def delete_server_image_by_id(image_id):
    uri = server_uri + "deleteMemberServerImages" + "?memberServerImageNoList.1=" + image_id
    res = send_get_uri(uri)
    if res.status_code > 400 :
        return check_error_response(res.text);
    tree = elemTree.fromstring(res.text)
    return_message = tree.find("returnMessage").text
    return_code = tree.find("returnCode").text
    print(return_code)
    print(return_message)
    return return_code;

# valid_check
def server_valid_check(server_id):
    if get_server(server_id) is None:
        return False;
    else:
        return True;
    
# create server image once
def create_server_image_by_id_process(server_id, stime):
    if get_server_list() == "0":
        print("Fail to Call API")
        return None;
    # check server id is valid
    print("[create_server_image_by_id_process] check server id is valid ")
    if not server_valid_check(server_id) :
        print("server id " + server_id + " not exist")
        return None;
    
    # save before image no (for delete)
    print("\n\n[create_server_image_by_id_process]")
    before_image_list = get_server_image_by_id(server_id)
    
    # check server status (while 2min, req stop 3 times interval 5sec)
    print("\n\n[create_server_image_by_id_process] check server status (while 2min, req stop 3 times interval 5sec)")
    wait_time = 60 * 3 # 60sec * 3(min)
    timeout = time.time() + wait_time
    while True:
        server_status = get_server(server_id)
        print("server_status = " + server_status)
        if (int(timeout) - int(time.time()))%(wait_time/3) == 0:
            time.sleep(stime)
            stop_status = stop_server_by_id(server_id)
            print("try stop server status = " + stop_status)
        if server_status == 'NSTOP' or time.time() > timeout:
            break
        time.sleep(stime)
    
    # request backup image and wait for stop status
    print("\n\n[create_server_image_by_id_process] request backup image and wait for stop status")
    timeout = time.time() + wait_time
    while True:
        server_op_status = get_server_op(server_id)
        print("server_op_status = " + server_op_status)
        if (int(timeout) - int(time.time()))%(wait_time/2) == 0:
            time.sleep(stime)
            server_image_status = create_server_image_by_id(server_id)
            print("try create server image status = " + server_image_status)
        if server_op_status == 'NULL' or time.time() > timeout:
            break
        time.sleep(stime)
        
    # print image status
    print("\n\n[create_server_image_by_id_process] print image status")
    after_image_list = get_server_image_by_id(server_id)
    print("success to copy image, now delete old images")
    for server_image_no in before_image_list:
        time.sleep(stime)
        delete_server_image_by_id(server_image_no)
        time.sleep(stime)
    
    # wait for server finish copy image
    print("\n\n[create_server_image_by_id_process] wait for server finish copy image")
    while True:
        server_op_status = get_server_op(server_id)
        print("server_op_status = " + server_op_status)
        if server_op_status == 'NULL' or time.time() > timeout:
            break
        time.sleep(stime)
    
    # start server
    print("\n\n[create_server_image_by_id_process] start server")
    timeout = time.time() + wait_time
    while True:
        server_op_status = get_server_op(server_id)
        print("server_status = " + server_op_status)
        if (int(timeout) - int(time.time()))%(wait_time/3) == 0:
            time.sleep(stime)
            start_status = start_server_by_id(server_id)
            print("try start server status = " + start_status)
        if server_op_status == 'NULL' or time.time() > timeout:
            break
        time.sleep(stime)
    
    # check server started
    print("\n\n[create_server_image_by_id_process] check server started")
    timeout = time.time() + wait_time
    while True:
        server_status = get_server(server_id)
        print("server_status = " + server_status)
        if server_status == 'RUN' or time.time() > timeout:
            break
        if server_status == 'NSTOP' and         (int(timeout) - int(time.time()))%(wait_time/3) == 0:
            time.sleep(stime)
            start_status = start_server_by_id(server_id)
            print("try start server status = " + start_status)
        time.sleep(stime)

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ID', type=str, default="2177996",
                        help="input server-id, default = 2177996")
    parser.add_argument('STIME', type=str, default="30",
                        help="input delay time for ncp api server, default = 30")
    args = parser.parse_args()
    ID = args.ID
    STIME = args.STIME
    try:
        create_server_image_by_id_process(ID, STIME)
    except:
        print("[API Server error]")
        
if __name__=="__main__":
    main()

