import inspect
import asyncio
from functools import wraps

def eventhandler(func):
	@wraps(func)
	def wrapper_func(*args, **kw):
		if inspect.iscoroutinefunction(func):
			return asyncio.gather(func(*args, **kw))
		return func(*args, **kw)
	return wrapper_func

