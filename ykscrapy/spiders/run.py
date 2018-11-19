from scrapy import cmdline

cmdline.execute("scrapy crawl youku -o t2.json".split())
#'str' object doesn't support item deletion