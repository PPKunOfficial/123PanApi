import requests

ApiUrl123 = [
    "https://www.123pan.com/a/api/",
    "https://www.123pan.com/b/api/"
]

# 获得用户状态


def getInfo(reSession):
    infoUrl = ApiUrl123[0]+"/user/info"
    afloginHeaders = {
        "content-type": "application/json;charset=UTF-8",
        "authorization": authorizationData,
        "user-agent": chrome_ua
    }
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
