import inspect
import asyncio
from functools improt wraps

def eventhandler(func):
	@wraps(func)
	def wrapper_func(*args, **kw):
		if inspect.inspect.iscoroutinefunction(func):
			return asyncio.gather(func(*args, **kw))
		return func(*args, **kw)
	return wrapper_func

