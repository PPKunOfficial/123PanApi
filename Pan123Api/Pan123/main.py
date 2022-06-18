from typing_extensions import Self
from fake_useragent import UserAgent
from . import login
import requests
# 随机UserAgent


class Pan123:
    def __init__(self):
        self.searchData = {
            "driveId": "0",
            "limit": "100",
            "orderBy": "fileId",
            "orderDir": "desc",
            "parentFileId": "0",
            "trashed": "false"
        }
        self.FileInformation = {
            "driveId": "",  # 0 (疑问 文件夹id?
            "duplicate": "",  # 0 未知
            "etag": "",  # 文件md5
            "fileName": "",
            "parentFileId": "",  # 文件id 0(未知 parent不清指代
            "size": "",  # 文件大小
            "type": "0"  # 类型 0(未知
        }
        self.ApiUrl123 = [
            "https://www.123pan.com/a/api/",
            "https://www.123pan.com/b/api/"
        ]
        self.afloginHeaders = {
            "content-type": "application/json;charset=UTF-8",
            "authorization": authorizationData,
            "user-agent": self.ua
        }
        self.cache={}
        self.ua=UserAgent().chrome
        self.session=requests.Session()
        self.session.trust_env=False
    class User:
        def login(self,passport, password):
            loginUrl = self.ApiUrl123[0]+"user/sign_in"
            loginData = {
                "passport": passport,
                "password": password
            }
            loginHeaders = {
                "content-type": "application/json;charset=UTF-8",
                "user-agent": self.ua
            }

            loginRes = self.session.post(
                url=loginUrl, headers=loginHeaders, data=loginData).content.decode("utf-8")
            return loginRes
        def createAuthData(self,loginRes):
            self.authorizationData = "Bearer "+loginDict["data"]["token"]
            self.cookieData = {
                "username": userData["passport"],
                "authorToken": loginDict["data"]["token"]
            }
            self.afloginHeaders = {
                "content-type": "application/json;charset=UTF-8",
                "authorization": self.authorizationData,
                "user-agent": self.ua
            }