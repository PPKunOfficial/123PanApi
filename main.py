from distutils.command.upload import upload
from http.cookiejar import Cookie
import requests
import json
import hashlib
import os
import sys
from fake_useragent import UserAgent

userData = {  # 账号密码
    "passport": sys.argv[1],
    "password": sys.argv[2]
}

ApiUrl123 = [
    "https://www.123pan.com/a/api/",
    "https://www.123pan.com/b/api/"
]
FileInformation = {
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

reSession = requests.Session()
reSession.trust_env=False # 禁止信任环境变量

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
        url=loginUrl, headers=loginHeaders, data=loginData).content.decode("utf-8")
    return loginRes

# 创建验证数据


def createAuthData(loginRes, userData):
    loginDict = json.loads(loginRes)
    global authorizationData, cookieData, afloginHeaders  # 全局变量
    authorizationData = "Bearer "+loginDict["data"]["token"]
    cookieData = {
        "username": userData["passport"],
        "authorToken": loginDict["data"]["token"]
    }
    afloginHeaders = {
        "content-type": "application/json;charset=UTF-8",
        "authorization": authorizationData,
        "user-agent": chrome_ua
    }

# 获得用户状态


def getInfo():
    infoUrl = ApiUrl123[0]+"/user/info"
    infoRes = reSession.get(url=infoUrl, headers=afloginHeaders,
                            cookies=cookieData).content.decode('utf-8')
    return infoRes


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
    uploadReqData = FileInformation
    uploadReqData["driveId"] = "0"
    uploadReqData["duplicate"] = "0"
    uploadReqData["fileName"] = os.path.basename(fileDir)
    uploadReqData["parentFileId"] = "0"
    uploadReqData["size"] = os.path.getsize(fileDir)
    uploadReqData["type"] = "0"
    uploadReqData["etag"] = getFileMD5(filePath=fileDir)

    upRes = reSession.post(url=upReqUrl, data=uploadReqData, headers=afloginHeaders,
                           cookies=cookieData).content.decode('utf-8')
    return json.loads(upRes),uploadReqData["size"]

# 上传分段准备
def getUploadUrl(UploadInformation):
    upReqUrl = ApiUrl123[0]+"file/s3_list_upload_parts"
    uploadData={
        "bucket":UploadInformation["Bucket"],
        "key":UploadInformation["Key"],
        "uploadId":UploadInformation["UploadId"]
    }
    PartsRes = reSession.post(url=upReqUrl, data=uploadData, headers=afloginHeaders,
                           cookies=cookieData).content.decode('utf-8')
    return json.loads(PartsRes)

# 计算文件分段 一次put只上传10M即10485760字节
def compileFileSize(FileSize):
    FileSizeInt=FileSize//10485760
    if FileSizeInt*10485760!=FileSize:
        FileSizeInt+=1
    return FileSizeInt


loginRes = login(passport=userData["passport"], password=userData["password"])
createAuthData(loginRes=loginRes, userData=userData)
reqUploadRes=reqUpload(r"D:\Downloads\filebrowser.zip")
FileSize=reqUploadRes[1]
ReadyUploadInformation=getUploadUrl(reqUploadRes[0])
getUploadUrl(ReadyUploadInformation)
