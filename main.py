from http.cookiejar import Cookie
import requests
import json
import hashlib
import os
from fake_useragent import UserAgent

userData = {  # 账号密码
    "passport": "",
    "password": ""
}

ApiUrl123 = [
    "https://www.123pan.com/a/api/",
    "https://www.123pan.com/b/api/"
]
uploadInformation = {
    "driveId": "",  # 0 (疑问 文件夹id?
    "duplicate": "",  # 0 未知
    "etag": "",  # 文件md5
    "fileName": "",
    "parentFileId": "",  # 文件id 0(未知 parent不清指代
    "size": "",  # 文件大小
    "type": "0"  # 类型 0(未知
}
# e.g searchData URL
# https://www.123pan.com/b/api/file/list/new?driveId=0&limit=100&orderBy=fileId&orderDirection=desc&parentFileId=0&trashed=false
searchData = {
    "driveId": "0",
    "limit": "100",
    "orderBy": "fileId",
    "orderDir": "desc",
    "parentFileId": "0",
    "trashed": "false"
}

# 随机UserAgent
chrome_ua = UserAgent().chrome
print("这次使用的UA:", chrome_ua)

reSession = requests.Session()

class Pan123Api:
    # 登录
    def login(passport, password):
        loginUrl = ApiUrl123[0]+"/user/sign_in"
        loginData = {
            "passport": passport,
            "password": password
        }
        loginHeaders = {
            "content-type": "application/json;charset=UTF-8",
            "user-agent": chrome_ua
        }

        loginRes = reSession.post(
            url=loginUrl, headers=loginHeaders, data=loginData).content.decode('utf-8')
        return loginRes

    # 创建验证数据


    def createAuthData(loginRes, userData):
        loginDict = json.loads(loginRes)
        global authorizationData, cookieData, afloginHeaders  # 全局变量
        authorizationData = "Bearer "+loginDict["data"]["token"]
        cookieData = {
            "username": userData["passport"],
            "nickName": userData["passport"],
            "authorToken": loginDict["data"]["token"]
        }
        afloginHeaders = {
            "content-type": "application/json;charset=UTF-8",
            "authorization": authorizationData,
            "user-agent": chrome_ua
        }
        return authorizationData,cookieData,afloginHeaders

    # 获得用户状态


    def getInfo():
        infoUrl = ApiUrl123[0]+"/user/info"
        infoRes = reSession.get(url=infoUrl, headers=afloginHeaders,
                                cookies=cookieData).content.decode('utf-8')
        return infoRes

    # 获得文件列表


    def getDirInfo(searchData):
        DirInfoUrl = ApiUrl123[1]+"/file/list/new?driveId="+searchData["driveId"]+"&limit="+searchData["limit"]+"&orderBy="+searchData["orderBy"] + \
            "&orderDirection="+searchData["orderDir"]+"&parentFileId=" + \
            searchData["parentFileId"]+"&trashed="+searchData["trashed"]
        DirInfoRes = reSession.get(url=DirInfoUrl, headers=afloginHeaders,
                                cookies=cookieData).content.decode('utf-8')
        return DirInfoRes

    # 获取文件md5


    def getFileMD5(filePath):
        with open(filePath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    # 上传请求


    def reqUpload(fileDir):
        upReqUrl = ApiUrl123[1]+"file/upload_request"
        # 初始化上传参数
        uploadReqUrl = ApiUrl123[1]+"file/upload_request"
        uploadReqData = uploadInformation
        uploadReqData["driveId"] = "0"
        uploadReqData["duplicate"] = "0"
        uploadReqData["fileName"] = os.path.basename(fileDir)
        uploadReqData["parentFileId"] = "0"
        uploadReqData["size"] = os.path.getsize(fileDir)
        uploadReqData["type"] = "0"
        uploadReqData["etag"] = getFileMD5(filePath=fileDir)

        upRes = reSession.post(url=upReqUrl, data=uploadReqData, headers=afloginHeaders,
                            cookies=cookieData).content.decode('utf-8')
        return upRes

pan=Pan123Api()
loginRes = pan.login(passport=userData["passport"], password=userData["password"])
pan.createAuthData(loginRes=loginRes, userData=userData)
print(pan.reqUpload(r"D:\Downloads\filebrowser.zip"))
