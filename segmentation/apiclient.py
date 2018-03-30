#encoding:utf-8

import apibasic
import random
import json
import time
import requests
import urllib
import urllib2


'''
开放平台访问sdk
'''
class OpenApiClient:
	#基本场景参数
	GRANT_SCOPE="dev_client"
	GRANT_TYPE="client_credentials"
	
	def __init__(self,p_appId,p_appKey,p_secretKey):
		self.token = None
		self.refreshToken= None
		self.appId= self.make_app_id(p_appId)
		self.appKey= p_appKey
		self.secretKey = p_secretKey
		self.algoApiUrl="http://open-ai.yunos.com"
	
	'''
	 执行post请求，api为完整地址格式/api/后的部分
	 返回的为一个json结构，因为python的原因数据的中文部分都被编码 可以使用toPrintString转化为utf-8来解决
	'''
	def executePost(self,api,params,fileParams):
		self.beforeExecute()
		result = self.call_http_service("post",self.get_api_url(api),self.token,params,fileParams)
		if(not self.is_call_suc(result) and self.is_token_error(result)):
			self.refreshToken();
			result = self.call_http_service("post",self.get_api_url(api),self.token,params,fileParams)
		return result;
	'''
	执行post application/json请求
	'''
	def executePostJson(self,api,params):
		self.beforeExecute()
		result = self.executePostJsonSingle(self.get_api_url(api),self.token,params)
		if(not self.is_call_suc(result) and self.is_token_error(result)):
			self.refreshToken();
			result = self.executePostJsonSingle(self.get_api_url(api),self.token,params)
		return result;
	
	'''
	执行一次post json 请求
	'''
	def executePostJsonSingle(self,api,token,params):
		headers = {"Content-Type":"application/json;charset=utf-8","Authorization":"Bearer "+token}
		request = urllib2.Request(url=api, headers=headers, data=json.dumps(params))
		print "post =>"+api+":"+json.dumps(headers,ensure_ascii=False)+":"+json.dumps(params,ensure_ascii=False)
		response = urllib2.urlopen(request)
		return json.loads(response.read())
	'''
	 执行get请求，api为完整地址格式/api/后的部分
	 返回的为一个json结构，因为python的原因数据的中文部分都被编码 可以使用toPrintString转化为utf-8来解决
	'''
	def executeGet(self,api,params,fileParams):
		self.beforeExecute()
		result = self.call_http_service("get",self.get_api_url(api),self.token,params,fileParams)
		if(not self.is_call_suc(result) and self.is_token_error(result)):
			self.refreshToken();
			result = self.call_http_service("get",self.get_api_url(api),self.token,params,fileParams)
		return result;
	
	#是否是token过期引起的错误
	def is_token_error(self,resultJson):
		code = self.read_error_code(resultJson)
		if(not code is None):
			return code == "20202" or code == "20103"
		return False
	# 在执行之前需要检查参数
	def beforeExecute(self):
		if(self.token is None):
			self.grant_token()
	
	# 刷新token
	def refreshToken(self):
		self.grant_token()
	#http访问方法封装
	def	call_http_service(self,method,url,token,params,fileParams):
		systemHead = {"v":"v1","nonce":random.randint(0, 200),"timestamp":int(round(time.time() * 1000)),"appId":self.appId,"_c_v_":"py_v_1"}
		httpHeaders={}
		httpParams={}
		httpFileParams={}
		if(not token is None):
			if(method.lower() == 'post'):
				httpHeaders = {"Authorization":"Bearer "+token}
			else:
				httpHeaders = {"Authorization":"Bearer "+token}
		if(not params is None):
			httpParams= params
		if(not fileParams is None):
			httpFileParams = fileParams;

		finalHttpParams = {}
		finalHttpParams.update(systemHead)
		if(not httpParams is None):
			finalHttpParams.update(httpParams)

		if(method.lower() == 'post'):
			print "post =>"+url+":"+json.dumps(httpHeaders,ensure_ascii=False)+":"+json.dumps(finalHttpParams,ensure_ascii=False)
			r = requests.post(url, data=finalHttpParams, headers=httpHeaders,files=httpFileParams)
		else:
			print "get =>"+url+":"+json.dumps(httpHeaders,ensure_ascii=False)+":"+json.dumps(finalHttpParams,ensure_ascii=False)
			r = requests.get(url, params=finalHttpParams, headers=httpHeaders)

		return r.json()
	#处理appId问题	
	def make_app_id(self,appId):
		if(appId.find("APP-") >= 0):
			return appId
		return "APP-"+appId
	#token 授权	
	def grant_token(self):
		grantSign = apibasic.get_grant_sign(self.appId,self.appKey,self.secretKey)
		grantParams = {"app_id":self.appId,"client_id":self.appKey,"scope":self.GRANT_SCOPE,"sign":grantSign,"grant_type":self.GRANT_TYPE}
		resultJson = self.call_http_service("get",self.get_auth_url(),None,grantParams,None);
		if(self.is_call_suc(resultJson)):
			self.token = self.read_data(resultJson,"token")
			self.refreshToken = self.read_data(resultJson,"refreshToken")
			return self.token
		else:
			errorStr = "grant token error code="+self.read_error_code(resultJson)+" msg="+self.read_error_msg(resultJson)
			raise Exception(errorStr.encode("utf-8"))
	
	'''
		token有效性校验
		返回为三个字段(sucess,ErroCode,ErrorMsg)，如果校验成功则isSuccess为true，其余字段为空
	'''
	def check_token(self,token):
		checkParam = {"token":token,"scope":self.GRANT_SCOPE,"appId":appId}
		result = self.call_http_service("get",self.get_auth_check_url(),None,checkParam,None);
		resultJson = result.json()
		print resultJson
		if(self.is_call_suc(resultJson)):
			return True,"","";
		else:
			return False,self.read_error_code(resultJson),self.read_error_msg(resultJson)
	#读取返回数据
	def read_data(self,resultJson,key):
		if((not resultJson is None) and (not resultJson.get("data") is None)):
			return resultJson.get("data").get(key);
		return None;
	#是否返回结果是成功的
	def is_call_suc(self,resultJson):
		code = self.read_error_code(resultJson)
		print code
		return (not resultJson is None) and (code is None or code == "10000")
	
	#读取错误码
	def read_error_code(self,resultJson):
		code = resultJson.get("code")
		if(code is None):
			code = resultJson.get("errorCode")
		return str(code)
	#读取错误消息
	def read_error_msg(self,resultJson):
		msg = resultJson.get("message");
		if(msg is None):
			msg = resultJson.get("errorMsg") 
		return msg
	## protocol access relate		
	def get_basic_url(self):
		return self.algoApiUrl;
	## 授权地址
	def get_auth_url(self):
		return self.get_basic_url()+"/oauth/2.0/access_token"
	def get_auth_check_url(self):
		return self.get_basic_url()+"/oauth/2.0/certify"
	## api地址
	def get_api_url(self,api):
		return self.get_basic_url()+"/api/"+api

def toPrintString(str):
	if(not str is None):
		return str.encode("utf-8");
##加密参数，防止中文乱码问题
def encodeParams(params):
	for k in params:
		params[k] = urllib.quote(params[k])
		




	


