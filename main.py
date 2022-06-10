from distutils.command.upload import upload
from http.cookiejar import Cookie
from msilib.schema import File
import requests
import json
import hashlib
import os
import sys
import threading
from fake_useragent import UserAgent

userData = {  # 账号密码
    "passport": sys.argv[1],
    "password": sys.argv[2]
}
uploadSteps = 5 # 上传步长，也可以视为多少个线程上传
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
reSession.trust_env = False  # 禁止信任环境变量

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
    """
{
	"code": 0,
	"message": "ok",
	"data": {
		"AccessKeyId": "ZC6D4sERThhBGZYibt7",
		"SecretAccessKey": "IO7X8K4Y1IRR0GZPLGKZSQ8BWXO2DOZHW8XIF8Z",
		"SessionToken": "k8+CXpHtfpMIJ6+UwzMerngFN8c07Aasg9g4BTrmxBztpnX4hpAxcPqXO2A+H5rYfh3qo+4m67/Iwt2KxTY/NQyOo998hnQvGSRr6EZ35aikN8gcUAd0BTqf8Nx7MfQZN/QFKx+HhwA58ExmWbI7ZyLJfS6iMt4cXQDU6Dz0/L+OWlUVCtQfw9YrTYIJGeZmYiBrXb8I89fmfPdVc9D0RnN5o041wrX7mi+ZljMF6RB4MKeSu5e/yezyyXkor2pZZRjo7/Me8iVQIbtK4/Vjy1ZaDbECJr6ZdOrciyeQNVDsJ27u4RrSnLm+9duMii3RDR7k28W3YfmgmIiVmlSOmJR6kfXJTi4N0TZ7E1ZgzVU7x5JTNYpjEENgOo0TLPKtV9M2cmVqk/JPP43D8Fgb+C7+LUjkWfyRIvjYg4yNjr+2/oDkQvDv9ysnQMrJaFmKbS5BO8px72ohcsgTOywwA9oTDyC9qdvNL/sB1RavFvlGygjWp7qXMdpIsQkaVhInBoPiemXiOsv1eRGHM8arT7FN3wSCwHl1ngj2X4Mm8UjZJKcJB9nqWJiTY1oMxm/Ean7nLv6MPujKkq3MpLfOa6vh66+mbcVe6JbjG1Hns7U=",
		"Expiration": "2022-06-10T16:53:58.209744851Z",
		"Key": "6619ae3d/1811970423-0/6619ae3d106e79496705014e77377338",
		"Bucket": "123-824",
		"FileId": 28554494,
		"Reuse": false,
		"Info": null,
		"UploadId": "2~XhJIs_Q1sLvDhQpvzoVfZafSg2_hET0",
		"DownloadUrl": ""
	}
}
    """
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
    return json.loads(upRes), uploadReqData["size"]

# 上传分段准备


def getUploadUrl(UploadInformation):
    upReqUrl = ApiUrl123[0]+"file/s3_list_upload_parts"
    """
{
	"code": 0,
	"message": "ok",
	"data": {
		"Parts": null
	}
}
    """
    uploadData = {
        "bucket": UploadInformation["Bucket"],
        "key": UploadInformation["Key"],
        "uploadId": UploadInformation["UploadId"]
    }
    PartsRes = reSession.post(url=upReqUrl, data=uploadData, headers=afloginHeaders,
                              cookies=cookieData).content.decode('utf-8')
    return json.loads(PartsRes)

# 计算文件分段 一次put只上传10M即10485760字节


def compileFileSize(FileSize):
    FileSizeInt = FileSize//10485760
    if FileSizeInt*10485760 != FileSize:
        FileSizeInt += 1
    return FileSizeInt

# 获得上传分段链接


def repareUpload(UploadInformation, start,end):
    upRepareUrl = ApiUrl123[0]+"file/s3_repare_upload_parts_batch"
    """
{
	"code": 0,
	"message": "ok",
	"data": {
		"presignedUrls": {
			"1": "https://file.123pan.com/123-824/6619ae3d/1811970423-0/6619ae3d106e79496705014e77377338?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=7JOMZG52GXC4KNYKCRUQ%2F20220610%2Fdefault%2Fs3%2Faws4_request&X-Amz-Date=20220610T163858Z&X-Amz-Expires=900&X-Amz-SignedHeaders=host&partNumber=1&uploadId=2~XhJIs_Q1sLvDhQpvzoVfZafSg2_hET0&x-id=UploadPart&X-Amz-Signature=92482015107177d492cca3c1e3fc3a807a572ac2f573e35e0d76b416bf7be310"
		}
	}
}
    """
    upRepareData = {
        "bucket": UploadInformation["Bucket"],
        "key": UploadInformation["Key"],
        "partNumberEnd": end,
        "partNumberStart": start,
        "uploadId": UploadInformation["UploadId"]
    }
    PartsRes = reSession.post(url=upRepareUrl, data=upRepareData, headers=afloginHeaders,
                              cookies=cookieData).content.decode('utf-8')
    return json.loads(PartsRes)

# 确认是否有缓存


def hasCache(UploadInformation):
    if(UploadInformation["data"]["Info"] == None or UploadInformation["data"]["Info"] == ""):
        return 0
    else:
        return 1

# 云端合并文件


def completeUpload(UploadInformation):
    upRepareUrl = ApiUrl123[0]+"file/s3_complete_multipart_upload"
    upRepareData = {
        "bucket": UploadInformation["Bucket"],
        "key": UploadInformation["Key"],
        "uploadId": UploadInformation["UploadId"]
    }
    PartsRes = reSession.post(url=upRepareUrl, data=upRepareData, headers=afloginHeaders,
                              cookies=cookieData).content.decode('utf-8')
    return json.loads(PartsRes)


loginRes = login(passport=userData["passport"], password=userData["password"])
createAuthData(loginRes=loginRes, userData=userData)
reqUploadRes = reqUpload(r"D:\Downloads\filebrowser.zip")
FileSize = reqUploadRes[1]

if(hasCache(reqUploadRes[0]) == 1):
    print("云端有缓存")
else:
    ReadyUploadInformation = getUploadUrl(reqUploadRes[0])
    getUploadUrl(ReadyUploadInformation)
    partsCount=compileFileSize(FileSize)
    downloadThreadList=[]
    for i in range(1,partsCount+1,uploadSteps):
        reqRepare=repareUpload(reqUploadRes[0],i,partsCount+1)
        partUrl=[]
        for x in range(i,partsCount+1):
            partUrl.append(reqRepare["data"]["presignedUrls"][str(x)])
        

