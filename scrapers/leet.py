from selenium import webdriver
from time import sleep
import requests, bs4, datetime
import html
import re
import pprint, json

chromedriver_path = 'C:\\Users\\callu_000\\Desktop\\chromedriver_win32\\chromedriver.exe' # Change this to your own chromedriver path!
webdriver = webdriver.Chrome(executable_path=chromedriver_path)


response = requests.get("https://leetcode.com/api/problems/algorithms/")

x = json.loads(response.text)['stat_status_pairs']
prob_list = []
for i in range(len(x)):
    prob_list.append(str(x[i]['stat']['question__title_slug']))


problem_dict = {}


def cleanhtml(raw_html):
  cleanr = re.compile('<[^<]*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

count = 0
for j, prob in enumerate(prob_list):
	try:
		webdriver.get('https://leetcode.com/problems/'+ prob)
		sleep(1.2)

		question = webdriver.find_element_by_xpath('//*[@id="app"]/div/div[2]/div/div/div[1]/div/div[1]/div[1]/div/div[2]/div/div[2]')

		all_children_by_css = question.find_elements_by_css_selector("*")
		all_children_by_xpath = question.find_elements_by_xpath(".//*")


		text = ""
		for i, child in enumerate(all_children_by_xpath):
			tag = all_children_by_xpath[i].tag_name
			if tag == "p" or tag == "pre" or tag == "ul":
				string = html.unescape(all_children_by_xpath[i].get_attribute('innerHTML')) + '\n'
				string = string.replace(u'\xa0', u' ')
				string = string.replace('<li>', '•')
				string = cleanhtml(string)
				text += string



		text3 = text.split("Example", 1)
		

		problem_dict[count] = {	"title": prob,
							"problem": text3[0],
							"example": "Example" + text3[1]}
		count += 1
	except:
		continue

with open('problems.json', 'w') as fp:
	json.dump(problem_dict, fp, indent=4)
# pprint.pprint(problem_dict)