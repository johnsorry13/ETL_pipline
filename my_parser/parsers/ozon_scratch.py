string = 'Главная/Каталог/Освещение/Фонарики/Фонари налобные/фонарь налобный светодиодный ФОТОН 3Вт IP54 RSH-700 оранжевый'

words = string.split('/')

category = {
    'level1' : words[0],
    'level2' : words[1],
    'level3' : words[2],
    'level4' : words[3],
    'level5': words[4],

}
print(category)

