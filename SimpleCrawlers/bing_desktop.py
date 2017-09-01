
import requests
import win32api

def main():
    print(win32api.GetSystemMetrics(0))
    print(win32api.GetSystemMetrics(1))
    #r = requests.get(r"http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US")
    #print(r.text)


if __name__ == "__main__":
    main()