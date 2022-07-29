# 登录

def login(username, password,reSession):
    loginUrl = "https://www.123pan.com/a/api/user/sign_in"
    loginData = {
        "passport": username,
        "password": password
    }
    loginHeaders = {
        "content-type": "application/json;charset=UTF-8"
    }

    loginRes = reSession.post(
        url=loginUrl, headers=loginHeaders, data=loginData).content.decode("utf-8")
    return loginRes

# 创建验证数据


def createAuthData(loginRes, userData):
    import json
    loginDict = json.loads(loginRes)
    authorizationData = "Bearer "+loginDict["data"]["token"]
    cookieData = {
        "username": userData["username"],
        "authorToken": loginDict["data"]["token"]
    }
    afloginHeaders = {
        "content-type": "application/json;charset=UTF-8",
        "authorization": authorizationData,
    }
    return authorizationData, cookieData, afloginHeaders

# 获得登录信息
def getUserInformation():
    import sys
    userData = {  # 账号密码
    "username": sys.argv[1],
    "password": sys.argv[2]
    }
    return userData

# 用户使用情况
def getInfo(reSession,Cookies,Auth):
    infoUrl = "https://www.123pan.com/a/api/user/info"
    infoRes = reSession.get(url=infoUrl, headers=Auth,
                            cookies=Cookies).content.decode('utf-8')
    return infoRes