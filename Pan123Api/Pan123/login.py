import requests

ApiUrl123 = [
    "https://www.123pan.com/a/api/",
    "https://www.123pan.com/b/api/"
]
# 登录


def login(passport, password,ua):
    loginUrl = ApiUrl123[0]+"user/sign_in"
    loginData = {
        "passport": passport,
        "password": password
    }
    loginHeaders = {
        "content-type": "application/json;charset=UTF-8",
        "user-agent": ua
    }

    loginRes = self.session.post(
        url=loginUrl, headers=loginHeaders, data=loginData).content.decode("utf-8")
    return loginRes,reSession

# 创建验证数据


def createAuthData(loginRes):
    loginDict = loginRes
    authorizationData = "Bearer "+loginDict["data"]["token"]
    cookieData = {
        "authorToken": loginDict["data"]["token"]
    }
    return {"authData": authorizationData,
            "cookieData": cookieData}
