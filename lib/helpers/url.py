import re
import requests

def validate(in_str):
	urls = re.findall("https?:\/\/\S+\.\S+", in_str)
	if len(urls) > 2 or len(urls) == 0:
		return False
	try:
		r = requests.get(urls[0])
	except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
		raise e
		return False

	return True
