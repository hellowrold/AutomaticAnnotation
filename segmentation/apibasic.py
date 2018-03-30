#encoding:utf-8

# 提供基础工具方法

import time
import hashlib
import base64
import re
import hmac
import random
import json
import requests
from urllib import quote

#场景部分定义
SIGN_SPLITER ="."
PLATFORM_SIGNATURE = "nui_open_v1_1" #
ENCODE_HEAD ="%2b1%2b"
ENCODE_REAL_HEAD ="+1+";
EXPIRED_TIME =1800

#基础配置结构定义
class TokenGrantConf:
	def __init__(self):
		self.platformSignature = PLATFORM_SIGNATURE
		self.expiredTime = EXPIRED_TIME
		self.appKey=""
		self.appId="";
		self.secretKey=""
		self.timestamp=(int(round(time.time() * 1000)))
		self.expiredTime=1800
		self.request="";
		self.method="";
		self.contentType="POST"
		self.secretSign=""
		
#获取基础授权签名	
def get_grant_sign(appId,appKey,secretKey):
	tokenConf = TokenGrantConf()
	tokenConf.appKey = appKey
	tokenConf.secretKey = secretKey
	tokenConf.appId=appId
	
	check_params(tokenConf)
	return encode_sign(get_grant_sign_str(tokenConf))
# 对返回结果进行encode
def encode_sign(sign):
	print "sign => "+sign
	return ENCODE_HEAD+quote(sign)

# 获得签名字符串
def get_grant_sign_str(tokenConf):
	tokenConf = set_default(tokenConf)
	signStr=""
	signStr= add_field(signStr,tokenConf.platformSignature,True)
	signStr= add_field(signStr,tokenConf.timestamp,True)
	signStr= add_field(signStr,tokenConf.expiredTime,True)
	signStr= add_field(signStr,tokenConf.appKey,True)
	
	secretStr=get_secret_sign(tokenConf)
	print "final-secret => "+secretStr
	signStr=add_field(signStr,secretStr,True)
	
	requestStr=get_request_sign(tokenConf)
	signStr=add_field(signStr,requestStr,True)
	#secretStr=add_field(signStr,tokenConf)
	
	signStr=add_field(signStr,get_sum_signature(tokenConf,secretStr,requestStr),False)
	
	return signStr
# 获得校验签名字符串
def get_sum_signature(tokenConf,secretSign,requestSign):
	signa_str=""
	signa_str = add_field(signa_str,tokenConf.platformSignature,True)
	signa_str = add_field(signa_str,tokenConf.appKey,True)
	signa_str = add_field(signa_str,tokenConf.timestamp,True)
	signa_str = add_field(signa_str,tokenConf.expiredTime,True)
	signa_str = add_field(signa_str,secretSign,True)
	request_str = tokenConf.platformSignature+ requestSign;
	signa_str = add_field(signa_str,request_str,False)
	print "sum-sign-str=>"+signa_str
	return get_secret_str(signa_str)
# 获得密匙签名字符串
def get_secret_sign(tokenConf):
	strD = tokenConf.platformSignature+str(tokenConf.timestamp)+tokenConf.appKey+tokenConf.secretKey
	print "secret-str =>"+strD;
	return get_secret_str(strD)

#获得字符串加密结果
def get_secret_str(str):
	return hmac.new(PLATFORM_SIGNATURE,str,hashlib.sha256).hexdigest();
#获得参数签名
def get_request_sign(request):
	return "";

#校验基本参数
def check_params(tokenConf):
	if(tokenConf is None):
		 raise Exception("conf is null")
	if(tokenConf.appKey is None):
		 raise Exception("appKey is null")
	if(tokenConf.secretKey is None):
		raise Exception("appSecret is null")
	if(tokenConf.platformSignature is None):
		raise Exception("appSecret is null")
#设置默认参数	
def set_default(tokenConf):
	if(tokenConf.platformSignature is None):
		tokenConf.platformSignature = PLATFORM_SIGNATURE
	if(tokenConf.expiredTime is None):
		tokenConf.expiredTime = 1800
	if(tokenConf.timestamp is None):
		tokenConf.timestamp = (int(round(time.time() * 1000)))
		
	return tokenConf;

#在字符串中添加域	
def add_field(signStr,data,needSpliter):
	if(data is None):
		data =""
	data = str(data).replace("\\.","")
	signStr = signStr + data
	if(needSpliter):
		return signStr+"."
	else:
		return signStr


	


