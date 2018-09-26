

import sys
import os
import requests
import time
import random
import datetime

import parse

def main():
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

    ofile_name = datetime.datetime.now().strftime(r"%Y_%m_%d") + ".csv"
    parse.write_header(ofile_name)

    session = requests.Session()
    districts = ("gulou", "jianye", "qinhuai", "xuanwu", "jiangning", "yuhuatai", "qixia", "pukou", "liuhe", "lishui", "gaochun")
    for district in districts:
        for num_room in range(1, 6):

            total_pages = 2**30
            page_id = 1
            while page_id <= total_pages:
                try:
                    response = session.get("https://nj.lianjia.com/ershoufang/{}/pg{}l{}/".format(district, page_id, num_room))
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
                    total_pages = parse.get_total_pages(response.text)
                    print("{} total list pages found in {} {}".format(total_pages, district, num_room))
                if total_pages < 0:
                    break

                infos = parse.parse(response.text)
                print("{} infos extracted from page {} {} {}".format(len(infos), district, num_room, page_id))
                for info in infos:
                    for key in info:
                        info[key] = info[key].replace('"', "'")

                    info["district_name"] = district_names[district]
                    parse.write_info(ofile_name, info)

                time.sleep(random.uniform(5, 15))
                page_id += 1


if __name__ == "__main__":
    assert sys.version_info.major > 2, "This script runs only in Python3"
    main()
