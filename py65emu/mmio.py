from py65emu.mmu import Block

class IncorrectTypeError(TypeError):
	def __init__(self,f,exp,got):
		super(IncorrectTypeError,self).__init__("Bad argument {!r}, expected type {!r} (got {!r})".format(f,exp,got))

class MMIORegister:
	""" A memory-mapped I/O register. Can be used for hypervisor-level tasks, as well as math registers. """
	def __init__(self):
		pass
	def write(self,val):
		""" Allows for handling of a write of val to this register."""
		pass
	def read(self):
		""" Allows for handling a read of this register. """
		return 0

class MMIOBlock(Block):
	""" A block of MMIORegister objects, mapped to memory addresses. """
	def __init__(self,start,handlers):
		self.handlers = handlers
		for handler in self.handlers:
			if not isinstance(handler,MMIORegister):
				raise IncorrectTypeError(handler,MMIORegister,type(handler))
		super(MMIOBlock,self).__init__(start,len(handlers),True)
	def reset(self,*args,**kwargs): return
	def write(self,addr,val):
		""" Delegates writes to MMIORegister.write. """
		self.handlers[self.getIndex(addr)].write(val)
	def read(self,addr):
		return self.handlers[self.getIndex(addr)].read()
