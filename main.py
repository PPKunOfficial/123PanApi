import requests
import pan_sct.user as puser
import pan_sct.upload as pupload

# 初始化log
import pan_sct.log as log
log=log.log

userData = puser.getUserInformation()
uploadSteps=5
reSession = requests.Session()

reSession=requests.Session()
loginRes = puser.login(username=userData["username"], password=userData["password"],reSession=reSession)
authorizationData, cookieData, afloginHeaders=puser.createAuthData(loginRes=loginRes, userData=userData)
log.i(loginRes)

fileDir=r""
reqUploadRes = pupload.askUpload(reSession,cookieData,afloginHeaders,fileDir)
fileInformation = reqUploadRes[1]
uploadInformation=reqUploadRes[0]
ifHasCache=pupload.hasCache(uploadInformation)
if(ifHasCache == 1):
    print("云端有缓存")
else:
    ReadyUploadInformation = pupload.getUploadUrl(reSession,cookieData,afloginHeaders,reqUploadRes[0])
    partsCount=pupload.cutFile(fileInformation)[0]
    if(ReadyUploadInformation["data"]["Parts"]!=None):
        for i in range(0,partsCount,uploadSteps):
            reqRepare=pupload.repareUpload(reSession,cookieData,afloginHeaders,reqUploadRes[0],i,i+uploadSteps)
            for x in range(int(i),int(i)+uploadSteps):
                upURL=reqRepare["data"]["presignedUrls"][str(x)]
                log.d("START UPLOAD")
                log.d(str(x)+"URL -> "+upURL)
                if fileInformation["fileSize"]<100485760:
                    pupload.uploadFile(reSession,upURL,fileDir,i)
                else:
                    pupload.uploadFile(reSession,upURL,fileDir,i)
    else:
        reqRepare=pupload.repareUpload(reSession,cookieData,afloginHeaders,reqUploadRes[0],1,2)
        upURL=reqRepare["data"]["presignedUrls"]["1"]
        log.d("START UPLOAD")
        log.d(str(1)+"URL -> "+upURL)
        pupload.uploadFile(reSession,upURL,fileDir,partsCount)
    log.d(pupload.completeUpload(reSession,cookieData,afloginHeaders,uploadInformation))
    log.d(pupload.finishUpload(reSession,cookieData,afloginHeaders,uploadInformation))
        

