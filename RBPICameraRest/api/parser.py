#!/usr/bin/env python

#  Copyright (C) 2013
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see http://www.gnu.org/licenses/.
#
#  Authors : Roberto Calvo <rocapal at gmail dot com>


import subprocess
import StringIO
from json import JSONEncoder
from django.utils import simplejson

class Command:
	def __init__(self, name, command, large_command, description):
		self.name = name
		self.command = command
		self.large_command = large_command
		self.description = description

	def set_options (self, options):
		self.options = options

	def __str__(self):
		str = self.name + "\n"
		str = self.command + "\n"	
		str += self.large_command + "\n"
		str += self.description + "\n"

		if (self.options != None):
			str += "Options: " + ','.join(self.options)			

		return str


lcommands = {}
options_index = 0
options_name = ['exposure', 'awb', 'imxfx', 'metering']

black_list = ["-?", "-v", "-d", "-n", "-p", "-o", "-f"]

boolean_commands = ["-vs","-vf", "-hf"]

def parse_command (line):

	global lcommands

	command = line.split(',')[0]

	if (command in black_list):
		return

	large_command = line.split(',')[1].split(':')[0].lstrip()[0:-1]
	desc = line.split(':')
	description = (desc[1:][0])[1:-1]
	
	c = Command (large_command[2:], command, large_command, description)
	
	if (command in boolean_commands):
		options = ['True', 'False']	
		c.set_options(options)

	key = large_command[2:]
	lcommands[key] = c


def parse_options (line):
	global lcommands, options_index, options_name

	options = line.split(',')
	lcommands[options_name[options_index]].set_options(options)

	options_index = options_index + 1

def parse ():

	global options_index

	p = subprocess.Popen('raspistill', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderror = p.communicate()

	lines = StringIO.StringIO(stderror)

	notes = False
	options_index = 0

	for line in lines:
		if line[0] == "-":
			parse_command(line)
		
		if (line == "Notes\n"):
			notes = True

		if (notes and len(line.split(','))>=4):
			parse_options (line)		
	

	return lcommands
