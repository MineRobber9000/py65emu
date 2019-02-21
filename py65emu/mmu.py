import array


class MemoryRangeError(ValueError):
	pass


class ReadOnlyError(TypeError):
	pass


class Block:
	def __init__(self, start, length, readonly=False, value=None, romOffset=0):
		""" A block of memory. """
		self.start = start
		self.length = length
		self.readonly = readonly
		self.value = value
		self.offset = romOffset
		self.reset(True)

	def reset(self, force=False):
		""" Resets memory block to initial state. """
		if self.readonly and (not force): return
		if type(self.value)==list:
			self.memory=pad([0 for x in range(self.offset)]+self.memory,self.length)
		elif type(self.value)==type(self.reset): # function
			self.memory=pad([0 for x in range(self.offset)]+[self.value(x+self.offset) for x in range(self.length)],self.length)
		elif self.value is not None:
			self.memory=pad([0 for x in range(self.offset)]+[(v&0xFF) for v in self.value.read()],self.length)
			self.value = self.memory[self.offset:]
		else:
			self.memory=pad([],self.length)

	def getIndex(self,addr):
		""" Gets index of address addr in this block. Assumes addr is in bounds. """
		return addr-self.start

	def write(self,addr,val):
		""" Set value at addr to val. """
		self.memory[self.getIndex(addr)]=(val&0xFF)

	def read(self,addr):
		""" Get value from address addr. """
		return self.memory[self.getIndex(addr)]

class MMU:
	def __init__(self, blocks):
		"""
        Initialize the MMU with the blocks specified in blocks.  blocks
        is a list of 3-tuples, (start, length, readonly, value, valueStart).

        """

		# Different blocks of memory stored seperately so that they can
		# have different properties.  Stored as dict of "start", "length",
		# "readonly" and "memory"
		self.blocks = []

		for b in blocks:
			self.addBlock(*b)

	def reset(self):
		"""
        In all writeable blocks reset all values to zero.
        """
		for b in self.blocks:
			if not b['readonly']:
				b['memory'] = array.array('B', [0] * b['length'])

	def addBlock(self, start, length, readonly=False, value=None, romOffset=0):
		"""
        Add a block of memory to the list of blocks with the given start address
        length. whether it is readonly or not and the starting value as either
        a file pointer, binary value or list of unsigned integers.  If the
        block overlaps with an existing block an exception will be thrown.

        """

		# check if the block overlaps with another
		for b in self.blocks:
			if ((
			    start + length > b['start']
			    and start + length < b['start'] + b['length']
			) or (
			    b['start'] + b['length'] > start
			    and b['start'] + b['length'] < start + length
			)):
				raise MemoryRangeError()

		newBlock = {
		    'start': start,
		    'length': length,
		    'readonly': readonly,
		    'memory': array.array('B', [0] * length)
		}

		# TODO: implement initialization value
		if type(value) == list:
			for i in range(len(value)):
				newBlock['memory'][i + romOffset] = value[i]

		elif value is not None:
			a = array.array('B')
			a.fromstring(value.read())
			for i in range(len(a)):
				newBlock['memory'][i + romOffset] = a[i]

		self.blocks.append(newBlock)

	def getBlock(self, addr):
		"""
        Get the block associated with the given address.
        """

		for b in self.blocks:
			if addr >= b['start'] and addr < b['start'] + b['length']:
				return b

		raise IndexError

	def getIndex(self, block, addr):
		"""
        Get the index, relative to the block, of the address in the block.
        """
		return addr - block['start']

	def write(self, addr, value):
		"""
        Write a value to the given address if it is writeable.
        """
		b = self.getBlock(addr)
		if b['readonly']:
			raise ReadOnlyError()

		i = self.getIndex(b, addr)

		b['memory'][i] = value & 0xff

	def read(self, addr):
		"""
        Return the value at the address.
        """
		b = self.getBlock(addr)
		i = self.getIndex(b, addr)
		return b['memory'][i]

	def readWord(self, addr):
		return (self.read(addr + 1) << 8) + self.read(addr)
