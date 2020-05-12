import re
import requests

def validate(in_str):
	urls = re.findall("https?:\/\/\S+\.\S+", in_str)
	if len(urls) != 1:
		print('!')
		return False
	try:
		r = requests.get(urls[0])
	except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
		print('!')
		raise e
		return False

	return True