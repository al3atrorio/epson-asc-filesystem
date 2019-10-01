import os
import json
from flask import Flask, request, render_template
import ipaddress
import string

config_valid = False
config_dict = {}

appflask = Flask(__name__, static_url_path="/pages", static_folder='/root/webserver/pages')

@appflask.route('/')
def index():
    return appflask.send_static_file('index.html')

@appflask.route('/getconfig', methods = ['GET'])
def getConfig():

    print(" [*] Getting Config")

    if config_valid == True:
        message = {
            'result': "success",
            'server_ip': config_dict['server_ip'],
            'rabbitmq_login': config_dict['rabbitmq_login'],
            'lwm2m_server_ip': config_dict['lwm2m_server_ip'],
            'lwm2m_bootstrap_ip': config_dict['lwm2m_bootstrap_ip'],
            'lwm2m_dtls_enable': config_dict['lwm2m_dtls_enable'],
            'lwm2m_dtls_identity': config_dict['lwm2m_dtls_identity'],
            'wifi_enable': config_dict['wifi_enable'],
            'wifi_ssid': config_dict['wifi_ssid']
        }
    else:
        message = {
            'result': "error"
        }

    return json.dumps(message)

def validateConfig(data):
    valid = True
    message = ""

    if not isValidIP(data['serverIp']):
        message += "<p>IP do servidor inválido.</p>"
        valid = False
    if len(data["amqpKey"]) > 0:
        if not isHex(data["amqpKey"]) or (len(data["amqpKey"]) != 16 and len(data["amqpKey"]) != 24 and len(data["amqpKey"]) != 32):
            message += "<p>Senha do Amqp inválida. Tem que ser em formato hexadecimal, tamanho 16, 24 ou 32.</p>"
            valid = False
    if len(data["rabbitmqLogin"]) == 0:
        message += "<p>Login do RabbitMQ inválido.</p>"
        valid = False
    if not isValidIP(data['lwm2mServerIp']):
        message += "<p>IP do Lwm2m inválido.</p>"
        valid = False
    if not isValidIP(data['lwm2mBootstrapIp']):
        message += "<p>IP do Bootstrap Lwm2m inválido.</p>"
        valid = False
    if len(data["lwm2mDtlsIdentity"]) == 0:
        message += "<p>Identidade do DTLS inválida.</p>"
        valid = False
    if len(data["lwm2mDtlsKey"]) > 0:
        if not isHex(data["lwm2mDtlsKey"]) or (len(data["lwm2mDtlsKey"]) != 16 and len(data["lwm2mDtlsKey"]) != 24 and len(data["lwm2mDtlsKey"]) != 32):
            message += "<p>Senha DTLS inválida. Tem que ser em formato hexadecimal, tamanho 16, 24 ou 32.</p>"
            valid = False
    if len(data["wifiSsid"]) == 0:
        message += "<p>Ssid do Wifi inválido.</p>"
        valid = False
    if len(data["wifiPsk"]) > 0:
        if len(data["wifiPsk"]) < 8 or len(data["wifiPsk"]) > 63:
            message += "<p>Senha Wifi inválida. Tem que ter tamanho entre 8 e 63 caracteres.</p>"
            valid = False

    return (valid, message)

def isValidIP(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except:
        return False
    return False

def isHex(s):
     hex_digits = set(string.hexdigits)
     return all(c in hex_digits for c in s)

@appflask.route('/setconfig', methods = ['POST'])
def routeDoUpdate():
    result = "success"
    data = request.get_json()
    print("Setting configuration")
    print(data)

    valid, message = validateConfig(data)
    if not valid:
        print(message.encode('utf-8'))
        response = {
            'result': "error",
            'message': message
        }    
        return json.dumps(response)

    #Updating current config, so next reloads will send the correct config
    config_dict['server_ip'] = data["serverIp"]
    if len(data["amqpKey"]) > 0:        
        config_dict['amqp_encryption_key'] = data["amqpKey"]    
    config_dict['rabbitmq_login'] = data["rabbitmqLogin"]
    if len(data["rabbitmqPassword"]) > 0:
        config_dict['rabbitmq_password'] = data["rabbitmqPassword"]
    config_dict['lwm2m_server_ip'] = data["lwm2mServerIp"]
    config_dict['lwm2m_bootstrap_ip'] = data["lwm2mBootstrapIp"]
    config_dict['lwm2m_dtls_enable'] = data["lwm2mDtlsEnable"]
    config_dict['lwm2m_dtls_identity'] = data["lwm2mDtlsIdentity"]
    if len(data["lwm2mDtlsKey"]) > 0:
        config_dict['lwm2m_dtls_key'] = data["lwm2mDtlsKey"]

    config_dict['wifi_enable'] = data["wifiEnable"]
    config_dict['wifi_ssid'] = data["wifiSsid"]
    if len(data["wifiPsk"]) > 0:
        config_dict['wifi_psk'] = data["wifiPsk"]

    #writing the config to the files
    try:
        f = open("/data/system_config", 'w')
        f.write('server_ip=' + config_dict["server_ip"] + '\n')
        f.write('amqp_encryption_key=' + config_dict["amqp_encryption_key"] + '\n')
        f.write('rabbitmq_login=' + config_dict["rabbitmq_login"] + '\n')
        f.write('rabbitmq_password=' + config_dict["rabbitmq_password"] + '\n')
        f.close()

        f = open("/data/update_config", 'w')
        f.write('lwm2m_server_ip=' + config_dict["lwm2m_server_ip"] + '\n')
        f.write('lwm2m_bootstrap_ip=' + config_dict["lwm2m_bootstrap_ip"] + '\n')
        f.write('lwm2m_dtls_enable=' + config_dict["lwm2m_dtls_enable"] + '\n')
        f.write('lwm2m_dtls_identity=' + config_dict["lwm2m_dtls_identity"] + '\n')
        f.write('lwm2m_dtls_key=' + config_dict["lwm2m_dtls_key"] + '\n')
        f.close()

        f = open("/data/wifi_config", 'w')
        f.write('wifi_enable=' + config_dict["wifi_enable"] + '\n')
        f.write('wifi_ssid=' + config_dict["wifi_ssid"] + '\n')
        f.write('wifi_psk=' + config_dict["wifi_psk"] + '\n')
        f.close()

    except Exception as e:
        print(e)
        result = "error"
        #Recover previous config (config_dict)

    message = {
        'result': result,
    }
    
    return json.dumps(message) 

def loadConfigFile():
    global config_valid
    try:
        f = open("/data/system_config")
        
        for lines in f:
            line = lines.strip()
            if line == "":
                continue
            items = line.split('=', 1)
            if len(items) == 2:
                config_dict[items[0]] = items[1]

        f = open("/data/update_config")
        
        for lines in f:
            line = lines.strip()
            if line == "":
                continue
            items = line.split('=', 1)
            if len(items) == 2:
                config_dict[items[0]] = items[1]

        f = open("/data/wifi_config")
        
        for lines in f:
            line = lines.strip()
            if line == "":
                continue
            items = line.split('=', 1)
            if len(items) == 2:
                config_dict[items[0]] = items[1]

        config_valid = True
    except Exception as e:
        print(e)
        config_valid = False

if __name__ == "__main__":

    loadConfigFile()

    print(config_dict)
   
    appflask.run(port=5000, host='0.0.0.0')
    #appflask.run(port=5000, host='0.0.0.0', ssl_context='adhoc')