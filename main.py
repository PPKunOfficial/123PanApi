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
cutSize=10485760
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
    uploadData = {
        "bucket": UploadInformation["data"]["Bucket"],
        "key": UploadInformation["data"]["Key"],
        "uploadId": UploadInformation["data"]["UploadId"]
    }
    PartsRes = reSession.post(url=upReqUrl, data=uploadData, headers=afloginHeaders,
                              cookies=cookieData).content.decode('utf-8')
    return json.loads(PartsRes)

# 计算文件分段 一次put只上传10M即10485760字节


def compileFileSize(FileDir,cutSize=10485760):
    FileSize=os.path.getsize(FileDir)
    FileSizeInt = FileSize//cutSize
    if FileSizeInt%cutSize != 0:
        FileSizeInt += 1
    return FileSizeInt,FileSize

# 获得上传分段链接


def repareUpload(UploadInformation, start,end):
    upRepareUrl = ApiUrl123[0]+"file/s3_repare_upload_parts_batch"
    upRepareData = {
        "bucket": UploadInformation["data"]["Bucket"],
        "key": UploadInformation["data"]["Key"],
        "partNumberEnd": end,
        "partNumberStart": start,
        "uploadId": UploadInformation["data"]["UploadId"]
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
        "bucket": UploadInformation["data"]["Bucket"],
        "key": UploadInformation["data"]["Key"],
        "uploadId": UploadInformation["data"]["UploadId"]
    }
    PartsRes = reSession.post(url=upRepareUrl, data=upRepareData, headers=afloginHeaders,
                              cookies=cookieData).content.decode('utf-8')
    return json.loads(PartsRes)

# 上传文件
def putFile(url,fileDir,parts,cutSize=10485760):
    start=(parts)*cutSize
    f=open(fileDir,"rb")
    f.seek(start)
    partFileData=f.read(cutSize)
    reSession.options(url)
    headers={
        "User-Agent":chrome_ua,
        "Content-Length":str(cutSize)
    }
    reSession.put(url,data=partFileData,headers=headers)

loginRes = login(passport=userData["passport"], password=userData["password"])
createAuthData(loginRes=loginRes, userData=userData)
fileDir=r""
reqUploadRes = reqUpload(fileDir)
FileSize = reqUploadRes[1]
if(hasCache(reqUploadRes[0]) == 1):
    print("云端有缓存")
else:
    ReadyUploadInformation = getUploadUrl(reqUploadRes[0])
    partsCount=compileFileSize(fileDir)[0]
    for i in range(0,compileFileSize(fileDir)[0],uploadSteps):
        reqRepare=repareUpload(reqUploadRes[0],i,partsCount+1)
        downloadThreadList=[]
        for x in range(i,partsCount):
            upURL=reqRepare["data"]["presignedUrls"][str(x)]
            tname=str(x)+"_Thread"
            if FileSize<100485760:
                t=threading.Thread(target=putFile,args=(upURL,fileDir,x,),name=tname)
            else:
                t=threading.Thread(target=putFile,args=(upURL,fileDir,x,FileSize,),name=tname)
            t.start()
            downloadThreadList.append(t)
        for t in downloadThreadList:
            t.join()
    completeUpload(reqUploadRes[0])
        

