from nltk import Counter

temp = []
temp2 = []
mas = [
            ['синий', 10],
            ['синий', 10],
            ['красный', 10],
            ['телефон', 5],
            ['телефон', 5],
            ['арбалет', 4],
            ['машина', 10]
      ]
mas2 = [2, 3, 5]
mas.sort()
for i in mas2:
    for el in mas[i:6]:
        if el not in temp:
            temp.append(el)
        else:
            for t in temp:
                if t[0] == el[0]:
                    t[1] = t[1] + el[1]
    temp2.append([i, temp])

print(temp2)
