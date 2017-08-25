
import requests

def main():
    r = requests.get(r"http://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US")
    print(r.text)


if __name__ == "__main__":
    main()