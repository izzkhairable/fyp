import json

from matplotlib.font_manager import json_dump

number_list = ['0.1', '0', '..2', '..3']

for num in number_list:
    try:
        parsenum = float(num)
        print(parsenum)
    except:
        if num.startswith('.'):
            print(float(num.replace('.', '')))
lol = '[{"supplier":"mouser", "url":"www.mouser.sg", "qty":2, "unit_price":5.33},{"supplier":"digikey", "url":"www.digikey.sg", "qty": 3, "unit_price":6.51}]'

print(json.loads(lol)[0])