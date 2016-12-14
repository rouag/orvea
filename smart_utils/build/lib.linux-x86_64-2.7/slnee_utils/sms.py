# -*- coding: utf-8 -*-

__author__ = 'maddouri'

import requests
import json

def send_sms(message, reciepient):
    """
    @Author : Maddouri
    :param message: str
    :return:
    """
    datas = {
        "Username": 966559193773,
        "Password": "Aa1122334455",
        "Tagname": "IT-Unaizah",
        "RecepientNumber": reciepient,
        "VariableList": "",
        "ReplacementList": "",
        "Message": message,
        "SendDateTime": 0,
        "EnableDR": False
    }
    headers = {'content-type': 'application/json'}
    url="http://api.yamamah.com/SendSMS"
    print(datas)
    r = requests.post(url, data=json.dumps(datas), headers=headers)
    print(r)
    return(r.text)

def delay_sms(reciepient,task_number=None, employee=None):

    message = u"""نعلمكم أنه تم التأخر في معالجة المعاملة رقم %s من قبل الموظف %s
""" % (task_number,employee)
    return  send_sms(message,reciepient)

def reception_sms(reciepient,txt):
    return  send_sms(txt,reciepient)

def urgent_transaction(reciepient,task_number=None):

    message = u"""تمت احالة المعاملة العاجلة رقم %s لكم""" % (task_number, )
    return  send_sms(message,reciepient)

def secret_transaction(reciepient,task_number=None):

    message = u"""تمت احالة المعاملة السرية رقم %s لكم""" % (task_number, )
    return  send_sms(message,reciepient)

# reception_sms(4)
#print urgent_transaction(reciepient="0538408562", task_number=4589)