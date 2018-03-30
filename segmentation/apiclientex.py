#encoding:utf-8

import apiclient

##弹外（阿里云环境使用）
class OpenApiClientEx(apiclient.OpenApiClient):
	def __init__(self,p_appId,p_appKey,p_secretKey):
			self.token = None
			self.refreshToken= None
			self.appId= self.make_app_id(p_appId)
			self.appKey= p_appKey
			self.secretKey = p_secretKey
			self.algoApiUrl="http://open-ai.alibaba.com"