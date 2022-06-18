import os
fileDir="rubbish.file"
fileSize=os.path.getsize("rubbish.file")
# 10485760
def compileFileSize(FileSize,cutSize):
    FileSizeInt = FileSize//cutSize
    if FileSizeInt%cutSize != 0:
        FileSizeInt += 1
    return FileSizeInt,FileSize

# 上传文件
def putFile(fileDir,parts,cutSize=10485760):
    start=(parts)*cutSize
    f=open(fileDir,"rb")
    f.seek(start)
    partFileData=f.read(cutSize)
    print(partFileData)

coutCount=compileFileSize(fileSize,10)

for i in range(compileFileSize(fileSize,10)[0]):
    putFile(fileDir,parts=i,cutSize=10)