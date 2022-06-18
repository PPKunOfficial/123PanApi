from Pan123Api import login
import sys
import json
userData = {  # 账号密码
    "passport": sys.argv[1],
    "password": sys.argv[2]
}
loginRes, loginSession = login.login(passport=userData["passport"], password=userData["password"])[0], login.login(passport=userData["passport"], password=userData["password"])[1]
loginJson = json.loads(loginRes)
authData, cookieData = login.createAuthData(loginJson)["authData"], login.createAuthData(loginJson)["cookieData"]
