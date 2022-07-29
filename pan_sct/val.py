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

