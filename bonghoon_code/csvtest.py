import pandas as pd

# memberFile = pd.read_csv('test_csv_file.csv')
# id,name,number=memberFile.loc[0]
# # print(name,id,number)
# row=memberFile.shape
# # col=col[0]
# # print(row[0])
# for i in range(memberFile.shape[0]):
#     id, name, number = memberFile.loc[i]
#     print(name)

softNum = list(map(int, input("원하는 소프트웨어 번호를 입력: 1.vim 2.filezilla 3.ftp 4.default-jdk 5.synaptic  입력예시: 1 3 4\n").split()))
print("softnum 리스트", softNum)