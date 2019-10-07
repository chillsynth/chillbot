import re


class Platforms:
	"""Class that represents all music release platforms whose url is allowed in a string"""

	supported_platforms = {
	"soundcloud": "https?:\/\/soundcloud\.com\/.+\/.+",
	"youtube": "https?:\/\/(www\.)?youtu(\.be|be\.com)\/.+",
	"bandcamp": "https?:\/\/.+\.bandcamp\.com\/.+\/.+",
	"spotify": "https?:\/\/open\.spotify\.com\/.+\/.+",
	"itunes": "https?:\/\/music\.apple\.com\/[a-z]{2}\/album\/.+\/\d+",
	"mthu": "https?:\/\/musicsthehangup\.com",
	"distrokid": "https?:\/\/distrokid\.com/hyperfollow\/.+\/.+",
	"fanlink": "https?:\/\/fanlink\.to\/.+",
	"lnkto": "https?://.+\.lnk\.to/.+",
	"audius": "https?:\/\/audius\.co\/.+\/.+",
	"smarturl": "https?:\/\/(smarturl\.it|hyperurl\.co)\/.+",
	}

	def __init__(self):
		pass

	@staticmethod
	def one_pltfrm_in_str(strn):
		matches = False
		for platform in Platforms.supported_platforms.values():
			if re.search(platform, strn):
				matches = True
			if len(re.findall("https?://", strn)) > 1:
				matches = False
				break
		return matches