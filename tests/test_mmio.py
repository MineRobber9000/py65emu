#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_mmio
----------------------------------
"""

import os
import unittest

from py65emu.mmu import MMU, Block
from py65emu.mmio import MMIORegister, MMIOBlock, IncorrectTypeError

class TestMMIO(unittest.TestCase):
	def setUp(self):
		pass

	def test_baseclass(self):
		m = MMU([Block(0x0000,0x0200),MMIOBlock(0xfe00,[MMIORegister()])])
		m.write(0xfe00,5) # no-op
		self.assertEqual(m.read(0xfe00),0)

	def test_square_register(self):
		class SquareRegister(MMIORegister):
			def __init__(self):
				self.v=0
			def write(self,val):
				self.v=((val**2)&0xFF)
			def read(self):
				return self.v
		m = MMU([MMIOBlock(0,[SquareRegister()])])
		m.write(0,2)
		self.assertEqual(m.read(0),4)
		m.write(0,5)
		self.assertEqual(m.read(0),25)

	def test_error_on_not_mmioreg(self):
		with self.assertRaises(IncorrectTypeError) as context:
			MMIOBlock(0,[5])

	def tearDown(self):
		pass


if __name__ == '__main__':
	unittest.main()
