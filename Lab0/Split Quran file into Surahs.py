import csv
import re
import string

txt = open('C:/Users/Sc/Desktop/Moodle Master2/My_Home_Works/IR/Lab1/pg10.txt', 'r', encoding='utf-8').read()
data = {}  # will contain the verse as keys and the context as a value string 


# #============================= cree surah dans fichier.csv ========================
# for item in range(1,115):
#     pattern = '^({}:\d+) ([A-z\s,;\'?!:\.\(\)]+)$'.format(item)
#     for x in re.finditer(pattern, txt, re.MULTILINE):
#         key, values = x.groups()
#         data[key] = values.replace('\n', '')
#     with open('surah_CSV/surah_{}.csv'.format(item), 'w', encoding='utf-8') as csvFile:
#         writer = csv.writer(csvFile, delimiter='|')  # Create an Object 'Writer'
#         writer.writerow(('verse', 'context'))
#         for key in data:
#             writer.writerow((key, data[key]))
#         data.clear()


# #============================= cree Bible Verses dans fichier.csv ========================
for item in range(1,115):
    pattern = '^({}:\d+) ([A-z\s,;\'?!:\.\(\)]+)$'.format(item)
    for x in re.finditer(pattern, txt, re.MULTILINE):
        key, values = x.groups()
        data[key] = values.replace('\n', '')
    with open('C:\\Users\\Sc\\Desktop\\Moodle Master2\\My_Home_Works\\IR\\Lab1\\Chapter_CSV\\Chapter_{}.csv'.format(item), 'w', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile, delimiter='|')  # Create an Object 'Writer'
        writer.writerow(('verse', 'context'))
        for key in data:
            writer.writerow((key, data[key]))
        data.clear()




#============================= cree surah dans fichier.txt ========================
# for item in range(1,115):
#     pattern = '^({}:\d+) ([A-z\s,;\'?!:\.\(\)]+)$'.format(item)
#     for x in re.finditer(pattern, txt, re.MULTILINE):
#         key, values = x.groups()
#         # data[key] = values.replace('\n', '')
#         # print(values.replace('\n', ''))
#         with open("C:\\Users\\Sc\\Desktop\\Moodle Master2\\My_Home_Works\\IR\\Lab1\\bible_verses\\Surah_{}.txt".format(item), "a") as f:
#             f.write(str(key)+ " | " +str(values) + "\n")
