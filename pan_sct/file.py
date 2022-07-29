def getDirInfo(reSession, Cookies, Auth, searchData):
    afloginHeaders = Auth
    cookieData = Cookies
    DirInfoUrl = "https://www.123pan.com/b/api/file/list/new?driveId="+searchData["driveId"]+"&limit="+searchData["limit"]+"&orderBy="+searchData["orderBy"] + \
        "&orderDirection="+searchData["orderDir"]+"&parentFileId=" + \
        searchData["parentFileId"]+"&trashed="+searchData["trashed"]
    DirInfoRes = reSession.get(url=DirInfoUrl, headers=afloginHeaders,
                               cookies=cookieData).content.decode('utf-8')
    return DirInfoRes

# 获取本地文件md5


def getFileMD5(filePath):
    import hashlib
    with open(filePath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def getFileInformation(filePath):
    import os
    return {
        "fileSize": os.path.getsize(filePath),
        "fileName": os.path.basename(filePath),
        "fileEtag": getFileMD5(filePath)
    }
