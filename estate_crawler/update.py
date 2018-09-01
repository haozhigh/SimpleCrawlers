

import sys
import requests
import re
import time

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
    p_total_pages = re.compile(pa("h2", "class", "total fl") + r"[^<>]*" + p("span") + r"([^<>]*)" + pc("span"))
    m_total_pages = p_total_pages.search(text)
    if m_total_pages == None:
        return -1
    else:
        return (int(m_total_pages.group(1).strip()) - 1) // 30 + 1

def parse(text):
    p_info_clear = re.compile(pa("div", "class", "info clear"))
    p_title = re.compile(pa("div", "class", "title") + r"\s*" + p("a") + r"([^<>]*)" + pc("a"))
    p_house = re.compile(pa("span", "class", "houseIcon") + r"[^<>]*" + pc("span") + r"\s*" + p("a") + r"([^<>]*)" + pc("a") + r"([^<>]*)" + pc("div"))
    p_position = re.compile(pa("span", "class", "positionIcon") + r"[^<>]*" + pc("span") + r"([^<>]*)" + p("a") + r"([^<>]*)" + pc("a"))
    p_follow = re.compile(pa("span", "class", "starIcon") + r"[^<>]*" + pc("span") + r"([^<>]*)" + pc("div"))
    p_subway = re.compile(pa("span", "class", "subway") + r"([^<>]*)" + pc("span"))
    p_taxfree = re.compile(pa("span", "class", "taxfree") + r"([^<>]*)" + pc("span"))
    p_haskey = re.compile(pa("span", "class", "haskey") + r"([^<>]*)" + pc("span"))
    p_total_price = re.compile(pa("div", "class", "totalPrice") + r"\s*" + p("span") + r"([^<>]*)" + pc("span"))
    p_unit_price = re.compile(pa("div", "class", "unitPrice") + r"\s*" + p("span") + r"([^<>]*)" + pc("span"))

    infos = list()
    for m_info_clear in p_info_clear.finditer(text):
        info = dict()
        info["title"] = ""
        info["district"] = ""
        info["rooms"] = ""
        info["area"] = ""
        info["direction"] = ""
        info["decoration"] = ""
        info["elevator"] = ""
        info["floors"] = ""
        info["location"] = ""
        info["followed"] = ""
        info["visited"] = ""
        info["time"] = ""
        info["subway"] = ""
        info["taxfree"] = ""
        info["haskey"] = ""
        info["total_price"] = ""
        info["unit_price"] = ""

        m_total_price = p_total_price.search(text, pos = m_info_clear.end())
        if m_total_price != None:
            info["total_price"] = m_total_price.group(1).strip()
        else:
            continue

        m_unit_price = p_unit_price.search(text, pos = m_info_clear.end())
        if m_unit_price != None:
            info["unit_price"] = m_unit_price.group(1).strip()[2:-4]


        m_title = p_title.search(text, pos = m_info_clear.end(), endpos = m_unit_price.start())
        if m_title != None:
            info["title"] = m_title.group(1).strip()

        m_house = p_house.search(text, pos = m_info_clear.end(), endpos = m_unit_price.start())
        if m_house != None:
            info["district"] = m_house.group(1).strip()
            spans = m_house.group(2).split("|")
            for span in spans:
                span = span.strip()
                if span.find("室") >= 0 or span.find("厅") >= 0:
                    info["rooms"] = span
                elif span.find("平米") >= 0:
                    info["area"] = span[:-2]
                elif span.find("东") >= 0 or span.find("南") >= 0 or span.find("西") >= 0 or span.find("北") >= 0:
                    info["direction"] = span
                elif span.find("装") >= 0:
                    info["decoration"] = span
                elif span.find("电梯") >= 0:
                    info["elevator"] = span

        m_position = p_position.search(text, pos = m_info_clear.end(), endpos = m_unit_price.start())
        if m_position != None:
            info["floors"] = m_position.group(1).strip()
            info["location"] = m_position.group(2).strip()

        m_follow = p_follow.search(text, pos = m_info_clear.end(), endpos = m_unit_price.start())
        if m_follow != None:
            spans = m_follow.group(1).split(r"/")
            info["followed"] = spans[0].strip()[0:-3]
            info["visited"] = spans[1].strip()[1:-3]
            info["time"] = spans[2].strip()
        
        m_subway = p_subway.search(text, pos = m_info_clear.end(), endpos = m_unit_price.start())
        if m_subway != None:
            info["subway"] = m_subway.group(1).strip()
        m_taxfree = p_taxfree.search(text, pos = m_info_clear.end(), endpos = m_unit_price.start())
        if m_taxfree != None:
            info["taxfree"] = m_taxfree.group(1).strip()
        m_haskey = p_haskey.search(text, pos = m_info_clear.end(), endpos = m_unit_price.start())
        if m_haskey != None:
            info["haskey"] = m_haskey.group(1).strip()

        infos.append(info)

    return infos


def main():
    session = requests.Session()

    district_names = {"gulou": "鼓楼",
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

    run_pass = int(input("Select run pass from 1-4: "))
    if run_pass == 1:
        districts = ("gulou", "jianye")
        ofile_name = "1.csv"
    elif run_pass == 2:
        districts = ("qinhuai", "xuanwu")
        ofile_name = "2.csv"
    elif run_pass == 3:
        districts = ("jiangning",)
        ofile_name = "3.csv"
    elif run_pass == 4:
        districts = ("yuhuatai", "qixia", "pukou", "liuhe", "lishui", "gaochun")
        ofile_name = "4.csv"
    else:
        print("Invalid run pass: {}".format(run_pass))
        return

    with open(ofile_name, 'w') as ofile:
        ofile.write("标题" + ",")
        ofile.write("区域" + ",")
        ofile.write("小区" + ",")
        ofile.write("户型" + ",")
        ofile.write("面积（平方米）" + ",")
        ofile.write("朝向" + ",")
        ofile.write("装修" + ",")
        ofile.write("电梯" + ",")
        ofile.write("楼高" + ",")
        ofile.write("地址" + ",")
        ofile.write("关注（人）" + ",")
        ofile.write("多少次带看" + ",")
        ofile.write("发布时间" + ",")
        ofile.write("地铁" + ",")
        ofile.write("免税" + ",")
        ofile.write("看房" + ",")
        ofile.write("总价（万元）" + ",")
        ofile.write("单价（元/平方米）" + "\n")

    for district in districts:
        for num_room in range(1, 6):

            total_pages = 2**30
            page_id = 1
            while page_id <= total_pages:
                response = session.get("https://nj.lianjia.com/ershoufang/{}/pg{}l{}/".format(district, page_id, num_room))
                if response.status_code != 200:
                    print("Request {} {} {} failed with status code {}".format(district, num_room, page_id, 200))

                # get number of list pages under filter conditions
                if total_pages == 2**30:
                    total_pages = get_total_pages(response.text)
                    print("{} total list pages found in {} {}".format(total_pages, district, num_room))
                if total_pages < 0:
                    break

                infos = parse(response.text)
                print("{} infos extracted from page {} {} {}".format(len(infos), district, num_room, page_id))
                for info in infos:
                    for key in info:
                        info[key] = info[key].replace('"', "'")

                    with open(ofile_name, 'a') as ofile:
                        ofile.write('"' + info["title"] + '"' + ",")
                        ofile.write('"' + district_names[district] + '"' + ",")
                        ofile.write('"' + info["district"] + '"' + ",")
                        ofile.write('"' + info["rooms"] + '"' + ",")
                        ofile.write('"' + info["area"] + '"' + ",")
                        ofile.write('"' + info["direction"] + '"' + ",")
                        ofile.write('"' + info["decoration"] + '"' + ",")
                        ofile.write('"' + info["elevator"] + '"' + ",")
                        ofile.write('"' + info["floors"] + '"' + ",")
                        ofile.write('"' + info["location"] + '"' + ",")
                        ofile.write('"' + info["followed"] + '"' + ",")
                        ofile.write('"' + info["visited"] + '"' + ",")
                        ofile.write('"' + info["time"] + '"' + ",")
                        ofile.write('"' + info["subway"] + '"' + ",")
                        ofile.write('"' + info["taxfree"] + '"' + ",")
                        ofile.write('"' + info["haskey"] + '"' + ",")
                        ofile.write('"' + info["total_price"] + '"' + ",")
                        ofile.write('"' + info["unit_price"] + '"' + "\n")

                time.sleep(3)
                page_id += 1


if __name__ == "__main__":
    assert sys.version_info.major > 2, "This script runs only in Python3"
    main()