# 字典如何删除键 字典如何更新 字典如何合并

name_age = {"Tom": 23, "Jack": 25, "Lucy": 26}

if "Tom" in name_age:
    tom_age = name_age.pop("Tom")

print(name_age)

name_age2 = {"Tom": 23, "Jack": 35, "Lucy": 36}

name_age.update(name_age2)

print(name_age)
