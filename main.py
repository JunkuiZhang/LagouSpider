import requests
import json
from bs4 import BeautifulSoup as BS
import re
import csv


class LagouSpider:

	def __init__(self, gj="应届毕业生", xl=None, jd=None, city=None, hangye=None):
		# 工作经验
		self.gj = gj
		# 学历
		self.xl = xl
		# 公司融资阶段
		self.jd = jd
		# 工作城市
		self.city = city
		# 公司所在行业
		self.hy = hangye
		self.cookie = None
		self.urls = []
		self.urls.append(self.generate_initial_url())
		self.urls.append(self.generate_main_url())

	def simplify_str_output(self, l0):
		_sep = "   "
		l1 = ""
		for l in l0:
			l1 += l + _sep
		return l1

	def get_default_arguments(self):
		url = "http://www.lagou.com/jobs/list_?px=default"
		header = {
			"Host": "www.lagou.com",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
			"Connection": "keep-alive"
		}
		response = requests.get(url, headers=header)
		soup = BS(response.text, "html.parser")
		res = soup.find_all("li", attrs={"class": "multi-chosen"})

		def simplify(l0):
			l0 = str(l0).split()
			l1 = ""
			for l2 in l0:
				l1 += l2
			return l1

		for r in res:
			sou = BS(str(r), "html.parser")
			_index = sou.find_all("span", attrs={"class": "title"})
			if _index:
				print("=="*20)
				class_index = re.findall('"title">(.*)</span', str(_index[0]))
				print(class_index[0])
			info = []
			for a in sou.find_all("a"):
				_info = re.findall('ascript:;">(.*)<iclass=', simplify(a))
				if _info:
					info.append(_info[0])
				else:
					pass
			print(self.simplify_str_output(info))
		return None

	def generate_initial_url(self):
		url0 = "http://www.lagou.com/jobs/list_?px=default"
		url1 = "#filterBox"
		if self.gj:
			url0 += "&gj=%s" % self.gj
		elif self.xl:
			url0 += "&xl=%s" % self.xl
		elif self.jd:
			url0 += "&jd=%s" % self.jd
		elif self.city:
			url0 += "&city=%s" % self.city
		elif self.hy:
			url0 += "&hy=%s" % self.hy
		else:
			pass
		return url0 + url1

	def generate_main_url(self):
		url0 = "http://www.lagou.com/jobs/positionAjax.json"
		url1 = "&needAddtionalResult=false"
		px = "default"
		if self.gj:
			url0 += "&gj=%s" % self.gj
		if self.xl:
			url0 += "&xl=%s" % self.xl
		if self.jd:
			url0 += "&jd=%s" % self.jd
		if self.hy:
			url0 += "&hy=%s" % self.hy
		if px:
			url0 += "&px=default"
		if self.city:
			url0 += "&city=%s" % self.city
		res = url0 + url1
		res0 = res.split("&")
		res = res0[0] + "?" + res0[1]
		if len(res0) > 2:
			for i in range(2, len(res0)):
				res += "&" + res0[i]
		return res

	def get_page_total_num(self):
		header = {
			"Host": "www.lagou.com",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
			"Connection": "keep-alive"
		}
		response = requests.get(self.urls[0], headers=header)
		soup = BS(response.text, "html.parser")
		res = soup.find_all("span", attrs={"class": "span totalNum"})
		return re.findall('Num">([0-9]*)</span', str(res))[0]

	def read_page_data(self, page_num, keyword=""):
		post_header = {
			"Host": "www.lagou.com",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
			"Connection": "keep-alive"
		}
		if page_num == 1:
			_first = True
		else:
			_first = False
		post_data = {
			"first": _first,
			"pn": str(page_num),
			"kd": keyword
		}
		if self.cookie:
			response = requests.post(self.urls[1], post_data, headers=post_header, cookies=self.cookie)
		else:
			response = requests.post(self.urls[1], post_data, headers=post_header)
		page_json = json.loads(response.text)
		self.cookie = response.cookies
		print(page_json)
		return page_json["content"]["positionResult"]["result"]

	def run(self, save_csv=False):
		total_page_num = int(self.get_page_total_num())
		if save_csv:
			f = open("data.csv", "w", newline="")
			w = csv.writer(f)
			w.writerow(["CompanyName", "CompanySize", "City", "Salary", "Industry"])
		for page_num in range(1, total_page_num + 1):
			data = self.read_page_data(page_num=page_num)
			for d in data:
				print("=="*20)
				total_company_name = d["companyShortName"]
				short_company_name = d["companyName"]
				print("公司名称：    " + total_company_name + "(" + short_company_name + ")")
				print("公司规模：    " + d["companySize"])
				print("所在城市：    " + d["city"])
				print("岗位名称：    " + d["positionName"])
				print("工作薪资：    " + d["salary"])
				print("所在行业：    " + d["industryField"])
				print("职业类型：    " + d["jobNature"])
				print("公司提供：    " + self.simplify_str_output(d["companyLabelList"]))
				print("工作福利：    " + d["positionAdvantage"])
				if save_csv:
					w.writerow([total_company_name + "(" + short_company_name + ")", d["companySize"],
						   d["city"], d["salary"], d["industryField"]])
		if save_csv:
			f.close()


if __name__ == '__main__':
	t = LagouSpider(hangye="金融", city="上海")
	print(t.run())