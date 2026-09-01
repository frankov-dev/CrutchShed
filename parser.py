import requests
from bs4 import BeautifulSoup
import json

url = "https://dekanat.lnu.edu.ua/cgi-bin/timetable.cgi?n=700&group=-3165"

response = requests.get(url)

response.encoding = "cp1251"

soup = BeautifulSoup(response.text, "html.parser")

schedule = []
current_date = None
lessons = []

for el in soup.find_all(["h4", "tr"]):
    if el.name == "h4":
        date_text = el.get_text(" ", strip=True)
        # Check if it looks like a date (e.g. 01.09.2026)
        if len(date_text) >= 10 and date_text[2] == '.' and date_text[5] == '.':
            if current_date:
                schedule.append({"date": current_date, "lessons": lessons})
            current_date = date_text[:10]
            lessons = []
    elif el.name == "tr" and current_date:
        cells = el.select("td")
        if len(cells) != 3:
            continue
            
        number = cells[0].get_text(strip=True)
        times = cells[1].get_text("\n", strip=True).split("\n")
        if len(times) != 2:
            continue
            
        start = times[0]
        end = times[1]
        
        lesson_cell = cells[2]
        lessons_in_pair = []
        
        names = lesson_cell.select(".p_name")
        types = lesson_cell.select(".p_type_name")
        teachers = lesson_cell.select(".t_name")
        groups = lesson_cell.select(".gr2_name")
        rooms = lesson_cell.select(".room_name")
        
        for i in range(len(names)):
            lessons_in_pair.append({
                "subject": names[i].get_text(" ", strip=True),
                "type": types[i].get_text(" ", strip=True) if i < len(types) else "",
                "teacher": teachers[i].get_text(" ", strip=True) if i < len(teachers) else "",
                "group": groups[i].get_text(" ", strip=True) if i < len(groups) else "",
                "room": rooms[i].get_text(" ", strip=True) if i < len(rooms) else ""
            })
            
        lessons.append({
            "number": int(number),
            "start": start,
            "end": end,
            "lessons": lessons_in_pair
        })

if current_date:
    schedule.append({"date": current_date, "lessons": lessons})

with open("schedule.json", "w", encoding="utf-8") as f:
    json.dump(schedule, f, ensure_ascii=False, indent=2)
