#!/usr/bin/env python

"""
DESC: Applies static analysis in order to validate a given database file.

$Author$
$Rev$

VERSION: 1.0.2

MODIFICATION LOG:
	2014/04/22 - klang - Version 1.0 released

	2014/06/05 - klang - Allowed integers for menu selections,
	                     Checks for size violations

	2014/06/06 - klang - Better handles missing parentheses
	
	2014/12/05 - klang - Help message
"""

import os
import re
import sys
import shlex
import difflib

class Token:
	def __init__(self, name, matches, line):
		self.name = name
		self.matches = matches
		self.line = line

	def __str__(self):
		return self.name + " (line: " + str(self.line) + ")"

	def full_text(self):
		return "".join([x.group() for x in self.matches])

	def full_text_w_num(self):
		return self.full_text() + " (line: " + str(self.line) + ")"

	#Combine tokens into complex tokens
	def add(self, other):
		"""
			Since we throw away the other token we don't
		really need the temporary variables, but let's not
		contaminate any data that we don't need to.

			What we are doing is putting the entirety of the
		other token's text and line numbers before the existing
		data of those types in this token. This is because we
		have to pop tokens off a stack to construct a complex
		token which means they are in reverse order. So by
		putting the added token at the front, we'll be in a
		left-to-right order at the end.
		"""
		temp_matches = list(other.matches)
		temp_matches.extend(self.matches)
		self.matches = temp_matches

		self.line = other.line



	# (Regex Match, "Token Type")
db_lexicon = (
	# Keywords
	(re.compile(r"field"),     "FIELD"),
	(re.compile(r"record"),    "RECORD"),
	(re.compile(r"grecord"),   "RECORD"),
	(re.compile(r"alias"),     "ALIAS"),
	(re.compile(r"info"),      "INFO"),

	# Values
	(re.compile(r"[A-Za-z][A-Za-z0-9_]*"), "NAME"),
	(re.compile(r'".*"'),                  "STRING"),
	(re.compile(r"[0-9]+"),                "NUMBER"),

	# Symbols
	(re.compile(r":"),  "COLON"),
	(re.compile(r","),  "COMMA"),
	(re.compile(r"{"),  "OPEN_BRACE"),
	(re.compile(r"}"),  "CLOSE_BRACE"),
	(re.compile(r"\("), "OPEN_PARENS"),
	(re.compile(r"\)"), "CLOSE_PARENS"),
	(re.compile(r"\$"), "DOLLAR_SIGN"),
)



"""
	dbd_lexicon has to parse through much larger files (iocxxxLinux.dbd is 34,000 lines),
so we are arranging the regexs by how common they are. Also, we'll tag all identifiers as
NAME, then narrow it down with a faster replacement to cut down on the number of regexs we
have to perform on every token.
"""

	# (Regex Match, "Token Type")
dbd_lexicon = (
	(re.compile(r"[A-Za-z][A-Za-z0-9_]*"), "NAME"),

	(re.compile(r"\("), "OPEN_PARENS"),
	(re.compile(r"\)"), "CLOSE_PARENS"),

	(re.compile(r'".*"'), "STRING"),

	(re.compile(r","),  "COMMA"),

	(re.compile(r"[0-9]+"), "NUMBER"),

	(re.compile(r"{"),  "OPEN_BRACE"),
	(re.compile(r"}"),  "CLOSE_BRACE"),

	(re.compile(r".*"), "CATCHALL"),
)

name_replace = {
	"field" :      "FIELD",
	"choice" :     "CHOICE",
	"menu" :       "MENU",
	"recordtype" : "RECORD_TYPE",
	"prompt" :     "PROMPT",
	"promptgroup" :"PROMPT_GROUP",
	"size":        "SIZE",
	"interest":    "INTEREST",
	"extra":       "EXTRA",
	"special" :    "SPECIAL",
	"initial" :    "INITIAL",
	"pp" :         "PP",
	"size" :       "SIZE",
	"base" :       "BASE",
	"asl" :        "ASL",
	"include" :    "INCLUDE",
}


base_db_grammar = {
	"FIELD" : {
		"OPEN_PARENS" : {
			"NAME" : {
				"COMMA" : "FIELD_DEFINITION"}}},

	"INFO" : {
		"OPEN_PARENS" : {
			"NAME" : {
				"COMMA" : "INFO_DEFINITION"}}},

	"ALIAS" : {
		"OPEN_PARENS" : {
			"STRING" : {
				"CLOSE_PARENS" : "DEFINED_ALIAS"}}},

	"RECORD" : {
		"OPEN_PARENS" : {
			"NAME" : {
				"COMMA" : "RECORD_DEFINITION"}}},

	"DOLLAR_SIGN" : {
		"OPEN_PARENS" : {
			"NAME" : {
				"CLOSE_PARENS" : "MACRO"}}},

	"MACRO" : {
		"DOLLAR_SIGN" : {
			"OPEN_PARENS" : {
				"NAME" : {
					"CLOSE_PARENS" : "MACRO"}}},
		"NAME" : "MACRO",
		"COLON" : "MACRO"},

	"NAME" : {
		"COLON" : "NAME",
		"NAME"  : "NAME",
		"DOLLAR_SIGN" : {
			"OPEN_PARENS" : {
				"NAME" : {
					"CLOSE_PARENS" : "MACRO"}}}},
}




base_dbd_grammar = {
	"MENU" : {
		"OPEN_PARENS" : {
			"NAME" : {
				"CLOSE_PARENS" : "MENU_DEFINITION" }}},

	"MENU_DEFINITION" : {
		"OPEN_BRACE" : "MENU_HEADER" },

	"CHOICE" : {
		"OPEN_PARENS" : {
			"NAME" : {
				"COMMA" : {
					"STRING" : {
						"CLOSE_PARENS" : "CHOICE_DEFINITION" }}}}},

	"RECORD_TYPE" : {
		"OPEN_PARENS" : {
			"NAME" : {
				"CLOSE_PARENS" : {
					"OPEN_BRACE" : "RECORD_TYPE_HEADER" }}}},

	"FIELD" : {
		"OPEN_PARENS" : {
			"NAME" : {
				"COMMA" : {
					"NAME" : {
						"CLOSE_PARENS" : {
							"OPEN_BRACE" : "FIELD_HEADER" }}}}}},

	"PROMPT" : {
		"OPEN_PARENS" : {
			"STRING" : {
				"CLOSE_PARENS" : "PROMPT_DEFINITION"}}},

	"SPECIAL" : {
		"OPEN_PARENS" : {
			"NAME" : {
				"CLOSE_PARENS" : "SPECIAL_DEFINITION"}}},

	"PROMPT_GROUP" : {
		"OPEN_PARENS" : {
			"NAME" : {
				"CLOSE_PARENS" : "PROMPT_GROUP_DEFINITION"}}},

	"SIZE" : {
		"OPEN_PARENS" : {
			"NUMBER" : {
				"CLOSE_PARENS" : "SIZE_DEFINITION"}}},

	"INTEREST" : {
		"OPEN_PARENS" : {
			"NUMBER" : {
				"CLOSE_PARENS" : "INTEREST_DEFINITION"}}},

	"EXTRA" : {
		"OPEN_PARENS" : {
			"STRING" : {
				"CLOSE_PARENS" : "EXTRA_DEFINITION"}}},

	"PP" : {
		"OPEN_PARENS" : {
			"BOOLEAN" : {
				"CLOSE_PARENS" : "PP_DEFINITION"}}},

	"ASL" : {
		"OPEN_PARENS" : {
			"NAME" : {
				"CLOSE_PARENS" : "ASL_DEFINITION"}}},

	"INITIAL" : {
		"OPEN_PARENS" : {
			"STRING" : {
				"CLOSE_PARENS" : "INITIAL_DEFINITION"}}},

	"INCLUDE" : {
		"STRING" : "INCLUDE_DBD"},
}



#Matches the end of field and record definitions
def search_parens(flags, starter, token_stream):
	assigned = None

	while token_stream:
		token = token_stream.pop(0)

		if token.name in ("MACRO", "NAME", "STRING", "NUMBER") and not assigned:

			#Warn about un-quoted value
			if token.name in ("MACRO", "NAME"):
				flags["non_string_val"].append(token)

			assigned = token

		elif token.name == "CLOSE_PARENS" and assigned:
			return starter.matches[2].group(), assigned.full_text()

		else:
			print "Unexpected token received: "
			print "\tToken: " + token.full_text_w_num()

			if assigned:
				print '\tExpected: ["CLOSE_PARENS"]'
			else:
				print '\tExpected: ["MACRO", "NAME", "STRING", "NUMBER"]'

			print
			token_stream.insert(0, token)
			return starter.matches[2].group(), None

	print "Reached end of file without matching parens"
	print "\tMatching: " + starter.full_text_w_num()
	print

	return starter.matches[2].group(), None

#Matches the closing brace of a definitions
def search_brace(flags, world, recordtype, recordname, starter, token_stream):
	while token_stream:
		token = token_stream.pop(0)

		if token.name == "FIELD_DEFINITION" or token.name == "INFO_DEFINITION":
			fieldname, fieldval = search_parens(flags, token, token_stream)

			if fieldval:
				if recordtype in world["RECORD_TYPES"].keys():
					check_fields(world, recordtype, recordname, fieldname, fieldval, token)
				elif recordtype not in flags["unknown_record_type"]:
					flags["unknown_record_type"].append(recordtype)

		elif token.name == "DEFINED_ALIAS":
			continue

		elif token.name == "CLOSE_BRACE":
			return

		else:
			print "Unexpected token received: "
			print "\tToken: " + token.full_text_w_num()
			print
			return

	print "Reached end of file without matching brace"
	print "\tMatching: " + starter.full_text_w_num()
	print


def check_fields(world, recordtype, recordname, fieldname, fieldval, token):
	if fieldname in world["RECORD_TYPES"][recordtype].keys():
		fieldtype = world["RECORD_TYPES"][recordtype][fieldname]["TYPE"]

		if "LENGTH" in world["RECORD_TYPES"][recordtype][fieldname].keys():

			if len(fieldval.strip('"')) > world["RECORD_TYPES"][recordtype][fieldname]["LENGTH"]:
				print "Field larger than allowed size: "
				print "\tRecord: " + recordname
				print "\tField: " + fieldname + " (line: " + str(token.line) + ")"
				print "\tReceived: " + fieldval
				print "\tAllowed Length: " + str(world["RECORD_TYPES"][recordtype][fieldname]["LENGTH"])
				print

		if fieldtype == "DBF_MENU":
			menuname = world["RECORD_TYPES"][recordtype][fieldname]["CHOICES"]

			if fieldval not in world["MENUS"][menuname]:
				try:
					selection = int(fieldval.strip('"'))
				except ValueError:
					selection = None

				if not selection or selection >= len(world["MENUS"][menuname]):
					print "Invalid menu choice: "
					print "\tRecord: " + recordname
					print "\tField: " + fieldname + " (line: " + str(token.line) + ")"
					print "\tReceived: " + fieldval
					close = difflib.get_close_matches(fieldval, world["MENUS"][menuname])

					if close:
						print "\tPerhaps you meant: " + str(close)

					print
	else:
		print "Unknown field:"
		print "\tRecord: " + recordname
		print "\tField Received: " + fieldname + " (line: " + str(token.line) + ")"
		print "\tPerhaps you meant: " + str(difflib.get_close_matches(fieldname, world["RECORD_TYPES"][recordtype].keys()))
		print

def create_menu(starter, token_stream):
	choices = []

	while token_stream:
		token = token_stream.pop(0)

		if token.name == "CHOICE_DEFINITION":
			choices.append(token.matches[4].group())

		elif token.name == "CLOSE_BRACE":
			return choices


def create_field(starter, token_stream):
	data = {}

	fieldname = starter.matches[2].group()
	data["TYPE"] = starter.matches[4].group()


	while token_stream:
		token = token_stream.pop(0)

		if token.name == "CLOSE_BRACE":
			return fieldname, data

		elif token.name == "MENU_DEFINITION":
			data["CHOICES"] = token.matches[2].group()

		elif token.name == "SIZE_DEFINITION":
			data["LENGTH"] = int(token.matches[2].group())


def create_recordtype(starter, token_stream):
	the_type = {}

	while token_stream:
		token = token_stream.pop(0)

		if token.name == "FIELD_HEADER":
			fieldname, field = create_field(token, token_stream)
			the_type[fieldname] = field

		elif token.name == "CLOSE_BRACE":
			return the_type




def match_grammar(world, token_stream):
	#To keep track of non-breaking problems
	warnings = {
		"non_string_val": [],
		"unknown_record_type": []}

	while token_stream:
		token = token_stream.pop(0)

		#A DB file is essentially just a list of record definitions
		if token.name == "RECORD_DEFINITION":
			recordtype, recordname = search_parens(warnings, token, token_stream)

			#Open brace means we'll start looking for fields
			if token_stream and token_stream[0].name == "OPEN_BRACE":
				token_stream.pop(0)

				search_brace(warnings, world, recordtype, recordname, token, token_stream)
		else:
			print "Unexpected token received: "
			print "\tToken: " + token.full_text_w_num()
			print '\tExpected: ["RECORD_DEFINITION"]'
			print

	return warnings


# Calls advanced grammar functions
def check_dbd(world, token_stream):
	while len(token_stream):
		token = token_stream.pop(0)

		if token.name == "MENU_HEADER":
			world["MENUS"][token.matches[2].group()] = create_menu(token, token_stream)

		elif token.name == "RECORD_TYPE_HEADER":
			world["RECORD_TYPES"][token.matches[2].group()] = create_recordtype(token, token_stream)

#Match a string to it's token type, returns the token type and the regex match of the string
def match(token, is_db):
	if is_db:
		lexicon = db_lexicon
	else:
		lexicon = dbd_lexicon

	for regex, tok_name in lexicon:
		thematch = regex.match(token)

		if thematch:

			if tok_name == "NAME" and is_db == False:
				return name_replace.get(thematch.group(), tok_name), [thematch]

			return tok_name, [thematch]

	return token, []


#Matches a list of strings to tokens, returns a list of tokens
def grammate(token_stream, is_db):
	if is_db:
		base_grammar = base_db_grammar
	else:
		base_grammar = base_dbd_grammar

	current_grammar = base_grammar

	#Output, list of tokens
	stack = []

	#How many matched tokens
	trail = 0

	while True:
		token = token_stream.get_token()

		if not token:
			return stack

		tok_name, tok_match = match(token, is_db)

		token = Token(tok_name, tok_match, token_stream.lineno)

		if tok_name in current_grammar and type(current_grammar[tok_name]) == str:
			token.name = current_grammar[tok_name]

			for _ in range(trail):
				token.add(stack.pop())

			current_grammar = base_grammar
			trail = 0


		#Matched to complex token
		if token.name in current_grammar:
			trail += 1
			current_grammar = current_grammar[token.name]

		#Doesn't have a complex form
		else:
			trail = 0
			current_grammar = base_grammar

		stack.append(token)


def print_warnings(dbd_init, warn):
	if warn["non_string_val"]:
		if len(warn["non_string_val"]) > 1:
			print "Warning: multiple non-quoted values found"
		else:
			print "Warning: non-quoted value found"

		for index, token in enumerate(warn["non_string_val"]):

			#Don't flood the screen with warnings
			if index + 1 > 10:
				print "\t..."
				break
			else:
				print "\t" + token.full_text_w_num()

		print

	if warn["unknown_record_type"] and dbd_init:
		if len(warn["unknown_record_type"]) > 1:
			print "Warning: multiple unknown record types found"
		else:
			print "Warning: unknown record type found"

		for index, record_type in enumerate(sorted(warn["unknown_record_type"])):

			if index + 1 > 10:
				print "\t..."
				break
			else:
				print "\t" + record_type

		print

def load_dbd(dbd=""):
	world = {
		"MENUS" : {},
		"RECORD_TYPES" : {},
		}

	if dbd:
		with open(dbd, "r") as the_file:
			token_stream = grammate(shlex.shlex(the_file), False)

		check_dbd(world, token_stream)

	return world



if __name__ == "__main__":
	if sys.argv[1] == "-h" or sys.argv[1] == "--help":
		print "validateDB.py database.db [definitions.dbd]"
		quit()
	
	if not (2 <= len(sys.argv) <= 3):
		print "Usage: validateDB.py database.db [definitions.dbd]"
		quit()

	if not os.path.isfile(sys.argv[1]):
		print "No such file"
		quit()

	#Use dbd file if defined
	if len(sys.argv) == 3:
		world = load_dbd(dbd=sys.argv[2])
		dbd_init = True
	else:
		world = load_dbd()
		dbd_init = False

	with open(sys.argv[1], "r") as the_file:
		token_stream = grammate(shlex.shlex(the_file), True)

	warn = match_grammar(world, token_stream)
	print_warnings(dbd_init, warn)

