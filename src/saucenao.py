import zlib
import json
import asyncio
from pysaucenao import SauceNao as Client, PixivSource, SauceNaoException

METADATA_NAMES = ['short_limit', 'long_limit', 'long_remaining', 'short_remaining']

clients = {}

def get_client(api_key):
	client = clients.get(api_key)
	if client is None:
		client = Client(api_key=api_key)
		clients[api_key] = client
	return client

# def call_async(coro):
# 	try:
# 		loop = asyncio.get_running_loop()
# 	except RuntimeError:
# 		return asyncio.run(coro)
# 	else:
# 		return loop.run_until_complete(coro)

class SauceNAO:
	def __init__(self, image_url, api_key):
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
		self.error_type = None

		self.data_keys = list(self.__dict__.keys())
		self.image_url = image_url
		self.public_link = f"http://saucenao.com/search.php?db=999&url={image_url}"
		self.api = get_client(api_key)

	def update_if_none(self, key, value):
		if value is not None and len(value) > 0 and getattr(self, key) is None:
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
			if i >= len(values): break
			setattr(self, key, values[i])

	def query(self):
		try:
			results = asyncio.run(self.api.from_url(self.image_url))
		except SauceNaoException as err:
			self.error_type = type(err).__name__.split('.').pop()
			return { 'error_type': self.error_type }

		if len(results) < 1:
			self.error_type = 'not_found'
			return { 'error_type': self.error_type }

		for result in results:
			if hasattr(result, 'material') and isinstance(result.material, list):
				self.update_if_none('material', result.material[0])

			if isinstance(result, PixivSource):
				self.update_if_none('member', result.author_name)
				self.update_if_none('pixev_art', result.author_url)
				self.update_if_none('pixev_src', result.url)
			elif result.index == 'deviantArt':
				self.update_if_none('author', result.author_name)
				self.update_if_none('deviantart_art', result.author_url)
				self.update_if_none('deviantart_src', result.url)
			else:
				self.update_if_none('creator', result.author_name)

			if isinstance(result.urls, list):
				for url in result.urls:
					if 'danbooru.donmai.us' in url:
						self.update_if_none('danbooru', url)
					elif 'gelbooru.com' in url:
						self.update_if_none('gelbooru', url)
					elif 'chan.sankakucomplex.com' in url:
						self.update_if_none('sankaku', url)

		metadata = {}
		for meta in METADATA_NAMES:
			metadata[meta] = getattr(results, meta)
		return metadata


		
