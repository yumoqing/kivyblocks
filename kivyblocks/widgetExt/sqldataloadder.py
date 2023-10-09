from .dataloader import DataLoader
from appPublic.sqlorAPI import runSQLIterator,DBPools,runSQLPaging
from twisted.internet import defer, reactor


class SQLDataLoader(DataLoader):
	def __init__(self,dbdesc,**kw):
		self.dbdesc = dbdesc
		super(DataLoader,self).__init__(**kw)
		
	def _run(self,ns):
		@runSQLIterator
		def _sql(db,ns):
			return self.dbdesc['sqldesc']
		
		d = [ i for i in self._sql(self.dbdesc['db'],ns) ]
		return d
	
	def loadData(self,ns):
		d = defer.maybeDeferred(self._run,ns)
		d.callback(self.dataLaoded)
		return d

class SQLPaggingLoader(SQLDataLoader):
	def _run(self,ns):
		@runSQLIterator
		def _sql(db,ns):
			return self.dbdesc['sqldesc']
		
		d = self._sql(self.dbdesc['db'],ns)
		return d
	