


import sys
import os
import requests
import time
import random
import datetime
import argparse
import re

# re pattern for a tag
def p(tag):
    return r"<\s*" + tag + r"[^<>]*>"

# re pattern for a tag with attribute
def pa(tag, attr, value):
    return r"<\s*" + tag + r"[^<>]*" + attr + r"\s*\=\s*[\'\"]\s*" + value + r"\s*[\'\"]\s*[^<>]*>"

# re pattern for a close tag
def pc(tag):
    return r"<\s*\/" + tag + r"\s*>"

def get_total_pages(text):
    p_total_pages = re.compile(p("h2") + r"\s*" + "共有" + r"\s*" + p("span") + r"([^<>]*)" + pc("span") + r"\s*" + r"套\S+在租房源" + r"\s*" + pc("h2"))
    m_total_pages = p_total_pages.search(text)
    if m_total_pages == None:
        return -1
    else:
        return (int(m_total_pages.group(1).strip()) - 1) // 30 + 1

def parse(text):
    p_info_panel = re.compile(pa("div", "class", "info-panel"))
    p_title = re.compile(p("h2") + r"\s*<\s*a[^<>]*title\s*=[^<>]*>([^<>]*)" + pc("a"))
    p_location = re.compile(pa("span", "class", "region") + r"([^<>]*)" + pc("span"))
    p_rooms = re.compile(pa("span", "class", "zone") + r"\s*" + p("span") + r"([^<>]*)" + pc("span") + r"\s*" + pc("span"))
    p_area_direction = re.compile(pa("span", "class", "meters") + r"([^<>]*)" + pc("span") + r"\s*" + p("span") + r"([^<>]*)" + pc("span"))
    p_neighbour_floors_year = re.compile(pa("div", "class", "con") + r"\s*" + p("a") + r"([^<>]*)" + pc("a") + r"\s*" + p("span") + r"[^<>]*" + pc("span") + r"([^<>]*)" + p("span") + r"[^<>]*" + pc("span") + r"([^<>]*)\s*" + pc("div"))
    p_price = re.compile(pa("div", "class", "price") + r"\s*" + pa("span", "class", "num") + r"([^<>]*)" + pc("span") + r"[^<>]*" + pc("div"))
    p_update_time = re.compile(pa("div", "class", "price-pre") + r"([^<>]*)" + pc("div"))
    p_visited = re.compile(pa("span", "class", "num") + r"\s*(\d+)\s*" + pc("span") + r"\s*人\s*" + pc("div") + r"\s*" + pa("div", "class", "col-look") + r"\s*看过此房\s*" + pc("div"))
    p_subway = re.compile(pa("span", "class", "fang-subway-ex") + r"\s*" + p("span") + r"([^<>]*)" + pc("span") + r"\s*" + pc("span"))
    p_decoration = re.compile(pa("span", "class", "decoration-ex") + r"\s*" + p("span") + r"([^<>]*)" + pc("span") + r"\s*" + pc("span"))
    p_available = re.compile(pa("span", "class", "haskey-ex") + r"\s*" + p("span") + r"([^<>]*)" + pc("span") + r"\s*" + pc("span"))
    p_private_balcony = re.compile(pa("span", "class", "independentBalcony-ex") + r"\s*" + p("span") + r"([^<>]*)" + pc("span") + r"\s*" + pc("span"))
    p_private_bathroom = re.compile(pa("span", "class", "privateBathroom-ex") + r"\s*" + p("span") + r"([^<>]*)" + pc("span") + r"\s*" + pc("span"))

    infos = list()
    for m_info_panel in p_info_panel.finditer(text):
        info = dict()
        info["title"] = ""
        info["location"] = ""
        info["rooms"] = ""
        info["area"] = ""
        info["direction"] = ""
        info["neighbour"] = ""
        info["floors"] = ""
        info["year"] = ""
        info["price"] = ""
        info["update_time"] = ""
        info["visited"] = ""
        info["subway"] = ""
        info["decoration"] = ""
        info["available"] = ""
        info["private_balcony"] = ""
        info["private_bathroom"] = ""

        m_visited = p_visited.search(text, pos = m_info_panel.end())
        if m_visited != None:
            info["visited"] = m_visited.group(1).strip()
        else:
            continue

        m_title = p_title.search(text, pos = m_info_panel.end(), endpos = m_visited.start())
        if m_title != None:
            info["title"] = m_title.group(1).strip()

        m_location = p_location.search(text, pos = m_info_panel.end(), endpos = m_visited.start())
        if m_location != None:
            info["location"] = m_location.group(1).strip()
            while info["location"].endswith("&nbsp;"):
                info["location"] = info["location"][:-6]

        m_rooms = p_rooms.search(text, pos = m_info_panel.end(), endpos = m_visited.start())
        if m_rooms != None:
            info["rooms"] = m_rooms.group(1).strip()
            while info["rooms"].endswith("&nbsp;"):
                info["rooms"] = info["rooms"][:-6]

        m_area_direction = p_area_direction.search(text, pos = m_info_panel.end(), endpos = m_visited.start())
        if m_area_direction != None:
            info["area"] = m_area_direction.group(1).strip()
            info["direction"] = m_area_direction.group(2).strip()
            while info["area"].endswith("&nbsp;"):
                info["area"] = info["area"][:-6].strip()
            if info["area"].endswith("平米"):
                info["area"] = info["area"][:-2]

        m_neighbour_floors_year = p_neighbour_floors_year.search(text, pos = m_info_panel.end(), endpos = m_visited.start())
        if m_neighbour_floors_year != None:
            info["neighbour"] = m_neighbour_floors_year.group(1).strip()
            info["floors"] = m_neighbour_floors_year.group(2).strip()
            info["year"] = m_neighbour_floors_year.group(3).strip()

        m_price = p_price.search(text, pos = m_info_panel.end(), endpos = m_visited.start())
        if m_price != None:
            info["price"] = m_price.group(1).strip()

        m_update_time = p_update_time.search(text, pos = m_info_panel.end(), endpos = m_visited.start())
        if m_update_time != None:
            info["update_time"] = m_update_time.group(1).strip()
            if info["update_time"].endswith(" 更新"):
                info["update_time"] = info["update_time"][:-3]

        m_subway = p_subway.search(text, pos = m_info_panel.end(), endpos = m_visited.start())
        if m_subway != None:
            info["subway"] = m_subway.group(1).strip()

        m_decoration = p_decoration.search(text, pos = m_info_panel.end(), endpos = m_visited.start())
        if m_decoration != None:
            info["decoration"] = m_decoration.group(1).strip()

        m_available = p_available.search(text, pos = m_info_panel.end(), endpos = m_visited.start())
        if m_available != None:
            info["available"] = m_available.group(1).strip()

        m_private_balcony = p_private_balcony.search(text, pos = m_info_panel.end(), endpos = m_visited.start())
        if m_private_balcony != None:
            info["private_balcony"] = m_private_balcony.group(1).strip()

        m_private_bathroom = p_private_bathroom.search(text, pos = m_info_panel.end(), endpos = m_visited.start())
        if m_private_bathroom != None:
            info["private_bathroom"] = m_private_bathroom.group(1).strip()

        infos.append(info)

    return infos

def write_header(ofile_name):
    with open(ofile_name, 'w') as ofile:
        ofile.write("标题" + ",")
        ofile.write("区域" + ",")
        ofile.write("小区" + ",")
        ofile.write("户型" + ",")
        ofile.write("面积（平方米）" + ",")
        ofile.write("朝向" + ",")
        ofile.write("附近" + ",")
        ofile.write("楼高" + ",")
        ofile.write("年限" + ",")
        ofile.write("价格" + ",")
        ofile.write("更新时间" + ",")
        ofile.write("多少人看过" + ",")
        ofile.write("地铁" + ",")
        ofile.write("装修" + ",")
        ofile.write("看房" + ",")
        ofile.write("独立阳台" + ",")
        ofile.write("独卫" + "\n")

def write_info(ofile_name, info):
    with open(ofile_name, 'a') as ofile:
        try:
            ofile.write('"' + info["title"] + '"' + ",")
            ofile.write('"' + info["district_name"] + '"' + ",")
            ofile.write('"' + info["location"] + '"' + ",")
            ofile.write('"' + info["rooms"] + '"' + ",")
            ofile.write('"' + info["area"] + '"' + ",")
            ofile.write('"' + info["direction"] + '"' + ",")
            ofile.write('"' + info["neighbour"] + '"' + ",")
            ofile.write('"' + info["floors"] + '"' + ",")
            ofile.write('"' + info["year"] + '"' + ",")
            ofile.write('"' + info["price"] + '"' + ",")
            ofile.write('"' + info["update_time"] + '"' + ",")
            ofile.write('"' + info["visited"] + '"' + ",")
            ofile.write('"' + info["subway"] + '"' + ",")
            ofile.write('"' + info["decoration"] + '"' + ",")
            ofile.write('"' + info["available"] + '"' + ",")
            ofile.write('"' + info["private_balcony"] + '"' + ",")
            ofile.write('"' + info["private_bathroom"] + '"' + "\n")
        except:
            ofile.write("\n")

def update(districts, city, url):

    ofile_name = "{}_rent_{}.csv".format(city, datetime.datetime.now().strftime(r"%Y_%m_%d"))
    write_header(ofile_name)

    session = requests.Session()
    for district in districts.keys():
        for num_room in range(1, 6):

            total_pages = 2**30
            page_id = 1
            while page_id <= total_pages:
                try:
                    response = session.get(url.format(district, page_id, num_room))
                except:
                    print("Request {} {} {} triggered exception".format(district, num_room, page_id))
                    session = requests.Session()
                    time.sleep(60)
                    continue
                if response.status_code != 200:
                    print("Request {} {} {} failed with status code {}".format(district, num_room, page_id, 200))
                    session = requests.Session()
                    time.sleep(20)
                    continue

                # get number of list pages under filter conditions
                if total_pages == 2**30:
                    total_pages = get_total_pages(response.text)
                    print("{} total list pages found in {} {}".format(total_pages, district, num_room))
                    if total_pages > 100:
                        total_pages = 100
                if total_pages < 0:
                    break

                infos = parse(response.text)
                print("{} infos extracted from page {} {} {}".format(len(infos), district, num_room, page_id))
                for info in infos:
                    for key in info:
                        info[key] = info[key].replace('"', "'")

                    info["district_name"] = districts[district]
                    write_info(ofile_name, info)

                time.sleep(random.uniform(5, 15))
                page_id += 1

def main():
    parser = argparse.ArgumentParser(description = "get secondhand house info from LJ")
    parser.add_argument("city", choices = ["nanjing", "beijing", "shanghai"])
    args = parser.parse_args()

    if args.city == "nanjing":
        districts = {"gulou": "鼓楼",
                      "jianye": "建邺",
                      "qinhuai": "秦淮",
                      "xuanwu": "玄武",
                      "yuhuatai": "雨花台",
                      "qixia": "栖霞",
                      "jiangning": "江宁",
                      "pukou": "浦口",
                      "liuhe": "六合",
                      "lishui": "溧水",
                      "gaochun": "高淳"}
        url = "https://nj.lianjia.com/zufang/{}/pg{}l{}/"
        update(districts, args.city, url)
    elif args.city == "beijing":
        districts = {"dongcheng": "东城",
                     "xicheng": "西城",
                     "chaoyang": "朝阳",
                     "haidian": "海淀",
                     "fengtai": "丰台",
                     "shijingshan": "石景山",
                     "tongzhou": "通州",
                     "changping": "昌平",
                     "daxing": "大兴",
                     "yizhuangkaifaqu": "亦庄开发区",
                     "shunyi": "顺义",
                     "fangshan": "房山",
                     "mentougou": "门头沟",
                     "pinggu": "平谷",
                     "huairou": "怀柔",
                     "miyun": "密云",
                     "yanqing": "延庆"}
        url = "https://bj.lianjia.com/zufang/{}/pg{}l{}/"
        update(districts, args.city, url)
    elif args.city == "shanghai":
        districts = {"pudong": "浦东",
                     "minhang": "闵行",
                     "baoshan": "宝山",
                     "xuhui": "徐汇",
                     "putuo": "普陀",
                     "yangpu": "杨浦",
                     "changning": "长宁",
                     "songjiang": "松江",
                     "jiading": "嘉定",
                     "huangpu": "黄浦",
                     "jingan": "静安",
                     "zhabei": "闸北",
                     "hongkou": "虹口",
                     "qingpu": "青浦",
                     "fengxian": "奉贤",
                     "jinshan": "金山",
                     "chongming": "崇明"}
        url = "https://sh.lianjia.com/zufang/{}/pg{}l{}/"
        update(districts, args.city, url)
    else:
        print("Unsupported city: {}".format(args.city))
        return


if __name__ == "__main__":
    assert sys.version_info.major > 2, "This script runs only in Python3"
    main()