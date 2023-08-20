import zlib
import json

class SauceNAO:
	def __init__(self, image_url):
		self.creator = None
		self.material = None
		self.author = None
		self.member = None
		self.deviantart_art = None
		self.deviantart_src = None
		self.pixev_art = None
		self.pixev_src = None
		self.gelbooru = None
		self.danbooru = None
		self.sankaku = None

		self.data_keys = list(self.__dict__.keys())
		self.saucenao_link = f"http://saucenao.com/search.php?db=999&url={image_url}"

	def update_if_none(self, key, value):
		if value is not None and getattr(self, key) is None:
			setattr(self, key, value)
	
	def is_empty(self):
		for key in self.data_keys:
			if getattr(self, key) is not None:
				return False
		return True

	def encode(self):
		values = [getattr(self, key) for key in self.data_keys]
		if all(value is None for value in values):
			return b''
		return zlib.compress(json.dumps(values).encode(), 1)

	def decode(self, bytestr):
		if bytestr == b'': return
		values = json.loads(zlib.decompress(bytestr))
		for i, key in enumerate(self.data_keys):
			setattr(self, key, values[i])
		
