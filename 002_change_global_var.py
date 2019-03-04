# 如何在函数内部修改全局变量-global 关键字

GLOBAL_NAME = "Hello"

print(GLOBAL_NAME)


def change_global_var():
    global GLOBAL_NAME
    GLOBAL_NAME = "world"
    print(GLOBAL_NAME)

change_global_var()
print(GLOBAL_NAME)
