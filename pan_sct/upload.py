# 上传请求
def askUpload(reSession,Cookies,Auth,fileDir):
    import json
    import pan_sct.file as pfile
    afloginHeaders=Auth
    cookieData=Cookies
    fileBaseInformation = {
        "driveId": "0",  # 0 (疑问 文件夹id?
        "duplicate": "0",  # 0 未知
        "etag": "",  # 文件md5
        "fileName": "",
        "parentFileId": "",  # 文件id 0(未知 parent不清指代
        "size": "",  # 文件大小
        "type": "0"  # 类型 0(未知
    }
    fileInformation=pfile.getFileInformation(fileDir)
    upReqUrl = "https://www.123pan.com/b/api/file/upload_request"
    uploadReqData = fileBaseInformation
    uploadReqData["driveId"] = "0"
    uploadReqData["duplicate"] = "0"
    uploadReqData["fileName"] = fileInformation["fileName"]
    uploadReqData["parentFileId"] = "0"
    uploadReqData["size"] = fileInformation["fileSize"]
    uploadReqData["type"] = "0"
    uploadReqData["etag"] = fileInformation["fileEtag"]

    upRes = reSession.post(url=upReqUrl, data=uploadReqData, headers=afloginHeaders,
                           cookies=cookieData).content.decode('utf-8')
    return json.loads(upRes), fileInformation

def getUploadUrl(reSession,Cookies,Auth,UploadInformation):
    import json
    upReqUrl = "https://www.123pan.com/a/api/file/s3_list_upload_parts"
    uploadData = {
        "bucket": UploadInformation["data"]["Bucket"],
        "key": UploadInformation["data"]["Key"],
        "uploadId": UploadInformation["data"]["UploadId"]
    }
    PartsRes = reSession.post(url=upReqUrl, data=uploadData, headers=Auth,
                              cookies=Cookies).content.decode('utf-8')
    return json.loads(PartsRes)

# 计算文件分段 一次put只上传10M即10485760字节
def cutFile(fileInformation,cutSize=10485760):
    FileSize=int(fileInformation["fileSize"])
    FileSizeInt = int(FileSize)//int(cutSize)
    if FileSizeInt%cutSize != 0:
        FileSizeInt += 1
    return FileSizeInt,FileSize

# 获得上传分段链接
def repareUpload(reSession,Cookies,Auth,UploadInformation, start,end):
    import json
    upRepareUrl = "https://www.123pan.com/a/api/file/s3_repare_upload_parts_batch"
    upRepareData = {
        "bucket": UploadInformation["data"]["Bucket"],
        "key": UploadInformation["data"]["Key"],
        "partNumberEnd": end,
        "partNumberStart": start,
        "uploadId": UploadInformation["data"]["UploadId"]
    }
    PartsRes = reSession.post(url=upRepareUrl, data=upRepareData, headers=Auth,
                              cookies=Cookies).content.decode('utf-8')
    return json.loads(PartsRes)

# 云端缓存
def hasCache(UploadInformation):
    if(UploadInformation["data"]["Info"] == None or UploadInformation["data"]["Info"] == ""):
        return 0
    else:
        return 1

# 云端合并文件
def completeUpload(reSession,Cookies,Auth,UploadInformation):
    import json
    upRepareUrl = "https://www.123pan.com/a/api/file/s3_complete_multipart_upload"
    upRepareData = {
        "bucket": UploadInformation["data"]["Bucket"],
        "key": UploadInformation["data"]["Key"],
        "uploadId": UploadInformation["data"]["UploadId"]
    }
    PartsRes = reSession.post(url=upRepareUrl, data=upRepareData, headers=Auth,
                              cookies=Cookies).content.decode('utf-8')
    return json.loads(PartsRes)

# 上传文件
def uploadFile(reSession,url,fileDir,parts,cutSize=10485760):
    start=(parts)*cutSize
    f=open(fileDir,"rb")
    f.seek(start)
    partFileData=f.read(cutSize)
    reSession.options(url)
    headers={
        "Content-Length":str(cutSize)
    }
    reSession.put(url,data=partFileData,headers=headers)

def finishUpload(reSession,Cookies,Auth,uploadInformation):
    import json
    upRepareUrl = "https://www.123pan.com/a/api/file/upload_complete"
    upRepareData = {
        "fileId":uploadInformation["data"]["FileId"]
    }
    PartsRes = reSession.post(url=upRepareUrl, data=upRepareData, headers=Auth,
                              cookies=Cookies).content.decode('utf-8')
    return json.loads(PartsRes)