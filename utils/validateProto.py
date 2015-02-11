#!/usr/bin/env python

"""
DESC: Applies static analysis in order to validate a given streams protocol file according to the
      file schema indicated throughout http://epics.web.psi.ch/software/streamdevice/doc/. Checks
      syntax as well as correct variable scoping.

$Author$
$Rev$

MODIFICATION LOG:
	2014/04/14 - klang - Version 1.0 released

	2015/02/11 - klang - Referencing protocols within other protocols no longer an error.
"""


import re
import sys
import shlex


class Token:
	def __init__(self, name, matches, lines):
		self.name = name
		self.matches = matches
		self.lines = lines

	def __str__(self):
		return self.name + " (line: " + str(self.lines[0]) + ")"

	def text(self, index):
		return self.matches[index].group(0) + " (line: " + str(self.lines[index]) + ")"

	def full_text(self):
		output = ""

		for match in self.matches:
			output += match.group(0)

		return output

	def full_text_w_num(self):
		return self.full_text() + " (line: " + str(self.lines[0]) + ")"

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

		temp_lines = list(other.lines)
		temp_lines.extend(self.lines)
		self.lines = temp_lines

	def add_back(self, other):
		self.matches.extend(other.matches)
		self.lines.extend(other.lines)


	# (Regex Match, "Token Type")
lexicon = (
    #Match special operators first
    (re.compile(r"(?i)out\b"),       "OUT"),
    (re.compile(r"(?i)in\b"),        "IN"),
    (re.compile(r"(?i)wait\b"),      "WAIT"),
    (re.compile(r"(?i)exec\b"),      "EXEC"),
    (re.compile(r"(?i)disconnect\b"),"DISCONNECT"),
    (re.compile(r"(?i)connect\b"),   "CONNECT"),
    (re.compile(r"(?i)event\b"),     "EVENT"),

    #System Variables
    (re.compile(r"(?i)LockTimeout\b"),  "SYS_VAR"),
    (re.compile(r"(?i)WriteTimeout\b"), "SYS_VAR"),
    (re.compile(r"(?i)ReplyTimout\b"),  "SYS_VAR"),
    (re.compile(r"(?i)ReadTimeout\b"),  "SYS_VAR"),
    (re.compile(r"(?i)PollPeriod\b"),   "SYS_VAR"),
    (re.compile(r"(?i)MaxInput\b"),     "SYS_VAR"),
    (re.compile(r"(?i)Terminator\b"),   "TERMINATOR"),
    (re.compile(r"(?i)InTerminator\b"), "TERMINATOR"),
    (re.compile(r"(?i)OutTerminator\b"),"TERMINATOR"),
    (re.compile(r"(?i)Separator\b"),    "SEPARATOR"),
    (re.compile(r"(?i)ExtraInput\b"),   "EXTRA_INPUT"),

    #Special Variables
    (re.compile(r"(?i)Error\b"),  "IGNORE_OR_ERROR"),
    (re.compile(r"(?i)Ignore\b"), "IGNORE_OR_ERROR"),

    (re.compile(r"(?i)true\b"),  "CONSTANT"),
    (re.compile(r"(?i)false\b"), "CONSTANT"),

    #Constants
	(re.compile(r"NUL\b"), "CONSTANT"),
    (re.compile(r"SOH\b"), "CONSTANT"),
    (re.compile(r"STX\b"), "CONSTANT"),
    (re.compile(r"ETX\b"), "CONSTANT"),
    (re.compile(r"EOT\b"), "CONSTANT"),
    (re.compile(r"ENQ\b"), "CONSTANT"),
    (re.compile(r"ACK\b"), "CONSTANT"),
    (re.compile(r"BEL\b"), "CONSTANT"),
    (re.compile(r"BS\b"),  "CONSTANT"),
    (re.compile(r"HT\b"),  "CONSTANT"),
    (re.compile(r"TAB\b"), "CONSTANT"),
    (re.compile(r"LF\b"),  "CONSTANT"),
    (re.compile(r"NL\b"),  "CONSTANT"),
    (re.compile(r"VT\b"),  "CONSTANT"),
    (re.compile(r"FF\b"),  "CONSTANT"),
    (re.compile(r"NP\b"),  "CONSTANT"),
    (re.compile(r"CR\b"),  "CONSTANT"),
    (re.compile(r"SO\b"),  "CONSTANT"),
    (re.compile(r"SI\b"),  "CONSTANT"),
    (re.compile(r"DLE\b"), "CONSTANT"),
    (re.compile(r"DC1\b"), "CONSTANT"),
    (re.compile(r"DC2\b"), "CONSTANT"),
    (re.compile(r"DC3\b"), "CONSTANT"),
    (re.compile(r"DC4\b"), "CONSTANT"),
    (re.compile(r"NAK\b"), "CONSTANT"),
    (re.compile(r"SYN\b"), "CONSTANT"),
    (re.compile(r"ETB\b"), "CONSTANT"),
    (re.compile(r"CAN\b"), "CONSTANT"),
    (re.compile(r"EM\b"),  "CONSTANT"),
    (re.compile(r"SUB\b"), "CONSTANT"),
    (re.compile(r"ESC\b"), "CONSTANT"),
    (re.compile(r"FS\b"),  "CONSTANT"),
    (re.compile(r"GS\b"),  "CONSTANT"),
    (re.compile(r"RS\b"),  "CONSTANT"),
    (re.compile(r"US\b"),  "CONSTANT"),
    (re.compile(r"DEL\b"), "CONSTANT"),
    (re.compile(r"SKIP\b"),"CONSTANT"),
    (re.compile(r"\?\b"),  "CONSTANT"),
    (re.compile(r"\*"),    "CONSTANT"),

    (re.compile(r"[A-Za-z][A-Za-z0-9_]*"), "NAME"),

    (re.compile(r"[0-9]+"),   "NUMBER"),
    (re.compile(r"0x[0-9]+"), "NUMBER"),

	(re.compile(r'"(.*)"'),   "STRING"), #Double-Quotes
	(re.compile(r"'(.*)'"),   "STRING"), #Single-Quotes

	(re.compile(r","),  "COMMA"),
	(re.compile(r"\-"), "DASH"),
    (re.compile(r"\$"), "DOLLAR_SIGN"),
	(re.compile(r"{"),  "OPEN_BRACE"),
	(re.compile(r"}"),  "CLOSE_BRACE"),
	(re.compile(r"\("), "OPEN_PARENS"),
	(re.compile(r"\)"), "CLOSE_PARENS"),
	(re.compile(r";"),  "SEMICOLON"),
	(re.compile(r"="),  "EQUALS"),
    (re.compile(r"@"),  "ERROR"),
    (re.compile(r".+"), "CATCHALL"),
)

# Token Type : Grammar   or   Token Type : "New Token Type"
base_grammar = {
	"NAME" : {
		#Shlex doesn't recognize dashes as part of names, so we'll have an advanced grammar take care of it
		"DASH"       : "COMPOUND_NAME",
		"OPEN_BRACE" : "FUNCTION_DEFINITION",
		"EQUALS"     : "ASSIGN_USER_VAR"},

	"DOLLAR_SIGN" : {
		"OPEN_BRACE" : {
			"NAME" : {
				"CLOSE_BRACE" : "VARIABLE"}},
		"NAME" : "VARIABLE"},


	"ERROR" : {
		"NAME" : {
			"OPEN_BRACE" : "ERROR_DEFINITION" }},

	"EXTRA_INPUT" : {
		"EQUALS" : "ASSIGN_EXTRA"},

	"TERMINATOR" : {
		"EQUALS" : "ASSIGN_TERMINATOR"},

	"SYS_VAR" : {
		"EQUALS" : "ASSIGN_SYS_VAR"},

	"SEPARATOR" : {
		"EQUALS" : "ASSIGN_SEPARATOR"},
}


# Matches correct types of values to the different types of variables
def branch_assignment(scope, starter, token_stream):
	if   starter.name == "ASSIGN_TERMINATOR":
		valid = ["STRING", "NUMBER", "VARIABLE", "CONSTANT"]
		repeats = True

	elif starter.name == "ASSIGN_SEPARATOR":
		valid = ["STRING", "NUMBER", "VARIABLE", "CONSTANT"]
		repeats = False

	elif starter.name == "ASSIGN_SYS_VAR":
		valid = ["NUMBER", "VARIABLE"]
		repeats = True

	elif starter.name == "ASSIGN_USER_VAR":
		valid = ["STRING", "NUMBER", "VARIABLE", "CONSTANT"]
		repeats = True

	#extraInput can only be set to Ignore or Error
	elif starter.name == "ASSIGN_EXTRA":
		valid = ["IGNORE_OR_ERROR"]
		repeats = False

	check_assignment(scope, starter, token_stream, valid, repeats)


# Checks the correct assignment statements
def check_assignment(scope, starter, token_stream, valid, repeats):

	#Last token matched
	assigned = None

	while len(token_stream):
		token = token_stream.pop(0)

		#Check for acceptable values
		if token.name in valid:

			#Check that any used variables are defined
			match_variable(scope, token)

			#Multiple consecutive tokens are allowed in certain assignments, but otherwise error
			if assigned and not repeats:
				print "Improper variable assignment: "
				print "\tVariable: " + starter.full_text_w_num()
				print "\tAssigning: " + token.text(0)
				print "\tBut already received: " + assigned.text(0)
				print

				token_stream.insert(0, token)
				return

			assigned = token

		#Semicolon only valid after a value has been given
		elif token.name == "SEMICOLON" and assigned:
			scope.append(starter.full_text().strip("${}= "))
			return

		else:
			if assigned:
				out_valid = valid + ["SEMICOLON"]
			else:
				out_valid = valid

			mismatch("Improper variable assignment:", valid, token)
			token_stream.insert(0, token)
			return


# If next token is a semicolon
def check_semicolon(scope, starter, token_stream):
	token = token_stream.pop(0)

	if not token.name == "SEMICOLON":
		mismatch("Unexpected token found: ", ["SEMICOLON"], token)
		token_stream.insert(0, token)


# If next token is a number
def check_number(scope, starter, token_stream):
	token = token_stream.pop(0)

	#Check that any used variables are defined
	match_variable(scope, token)

	if token.name not in ["NUMBER", "VARIABLE"]:
		mismatch("Unexpected token found: ", ["VARIABLE", "NUMBER"], token)
		token_stream.insert(0, token)
		return

	check_semicolon(scope, starter, token_stream)


# Match quotes and variables until semicolon
def check_string(scope, starter, token_stream):
	has_string = False

	while len(token_stream):
		#Semicolon only valid after some sort of value
		if token.name == "SEMICOLON" and has_string:
			return

		elif token.name in ("STRING", "VARIABLE"):
			#Check that any used variables are defined
			match_variable(scope, token)
			has_string = True

		else:
			mismatch("Unexpected token found: ", ["VARIABLE", "STRING"], token)
			token_stream.insert(0, token)
			return

	print "Reached end of file without finding semicolon:"
	print "\tFor: " + str(starter)
	print "\t\tText: " + starter.full_text()
	print


# Checks IN and OUT statements
def check_proto(scope, starter, token_stream):

	# Has there been at least one matched token since the last comma?
	comma_ok = False

	while len(token_stream):
		token = token_stream.pop(0)

		if token.name in ("NUMBER", "CONSTANT", "STRING", "VARIABLE"):
			#Check that any used variables are defined
			match_variable(scope, token)
			comma_ok = True

		#Comma only valid immediately after a value
		elif token.name == "COMMA" and comma_ok:
			comma_ok = False

		elif token.name == "SEMICOLON":
			return

		else:
			if comma_ok:
				valid = ["NUMBER", "CONSTANT", "VARIABLE", "STRING", "COMMA"]
			else:
				valid = ["NUMBER", "CONSTANT", "VARIABLE", "STRING"]

			mismatch("Improper protocol definition: " + str(starter), valid, token)
			token_stream.insert(0, token)
			return

		last_token = token

	print "Reached end of file without finding semicolon:"
	print "\tProtocol: " + str(starter)
	print


def check_event(scope, starter, token_stream):
	parens = 0
	assigned = None

	while len(token_stream):
		token = token_stream.pop(0)

		if assigned:
			if parens == 1:
				if token.name == "CLOSE_PARENS":
					parens += 1
					assigned = None
				else:
					mismatch("Improper event command: ", ["CLOSE_PARENS"], token)
					token_stream.insert(0, token)
					return
			else:
				if token.name == "SEMICOLON":
					return
				else:
					mismatch("Improper event command: ", ["SEMICOLON"], token)
					token_stream.insert(0, token)
					return
		else:
			if token.name == "OPEN_PARENS" and not parens:
				parens += 1

			elif token.name in ("VARIABLE", "NUMBER"):
				match_variable(scope, token)
				assigned = token

			else:
				mismatch("Improper event command: ", ["NUMBER", "VARIABLE"], token)
				token_stream.insert(0, token)
				return


def load_name(scope, starter, token_stream):
	curr = Token("NAME", starter.matches, starter.lines)

	while len(token_stream):
		token = token_stream.pop(0)

		#Any text is valid in a compound name
		if token.name in ("OUT", "IN", "WAIT", "EXEC", "DISCONNECT", "CONNECT", "EVENT", "SYS_VAR",
		                  "TERMINATOR", "SEPARATOR", "EXTRA_INPUT", "IGNORE_OR_ERROR", "CONSTANT",
		                  "NAME", "DASH", "NUMBER", "COMPOUND_NAME"):
			curr.add_back(token)
		elif token.name == "OPEN_BRACE" or token.name == "FUNCTION_DEFINITION":
			curr.name = "FUNCTION_DEFINITION"
			curr.add_back(token)
			token_stream.insert(0, curr)
			return
		elif token.name == "EQUALS":
			curr.name = "ASSIGN_USER_VAR"
			curr.add_back(token)
			token_stream.insert(0, curr)
			return
		elif token.name == "SEMICOLON":
			curr.name = "FUNCTION_REFERENCE"
			curr.add_back(token)
			token_stream.insert(0, curr)
			return
		else:
			token_stream.insert(0, token)
			token_stream.insert(0, curr)
			return

	print "Reached end of file without finishing name"
	print "\tName: " + curr.full_text_w_num()
	print


# Matches everything that can be within a definition until the matching close brace
def search_brace(scope, starter, token_stream, isError):
	myname = starter.full_text().strip().strip("{")

	#Has the protocol already been defined? Errors can be redefined
	if myname in scope and not isError:
		print "Attempting to redefine existing protocol:"
		print "\tProtocol: " + str(starter)
		print "\t\tName: " + myname
		print
	else:
		#If it isn't, it is now
		scope.append(myname)

	#Definitions have a copy of the global scope
	myscope = list(scope)

	# Only five valid error types
	if isError:
		name = starter.matches[1].group(0).lower()
		error_types = ["mismatch", "writetimeout", "replytimeout", "readtimeout", "init"]

		if name not in error_types:
			mismatch("Unknown error type: ", error_types, starter)
			return

	while len(token_stream):
		token = token_stream.pop(0)

		if token.name == "CLOSE_BRACE":
			return

		#Error definitions are only valid within a protocol definition
		elif token.name == "ERROR_DEFINITION" and not isError:
			search_brace(scope, token, token_stream, 1)

		elif "ASSIGN" in token.name:
			branch_assignment(scope, token, token_stream)

		elif token.name in ("OUT", "IN"):
			check_proto(scope, token, token_stream)

		elif token.name in ("CONNECT", "WAIT"):
			check_number(scope, token, token_stream)

		elif token.name == "EXEC":
			check_string(scope, token, token_stream)

		elif token.name == "DISCONNECT":
			check_semicolon(scope, token, token_stream)

		elif token.name == "EVENT":
			check_event(scope, token, token_stream)
		
		elif token.name in ("NAME", "COMPOUND_NAME"):
			load_name(scope, token, token_stream)
		
		elif token.name == "FUNCTION_REFERENCE":
			if token.full_text().strip().strip(";") not in scope:
				print "Referencing undefined protocol in definition:"
				print "\tReference: " + token.full_text_w_num()
				print
		
		else:
			extra_token(scope, token, token_stream)

	print "Reached end of file without finding matching brace:"
	print "\tFrom: " + str(starter)
	print "\t\tName: " + starter.full_text()
	print "\tOriginal brace on line: " + str(starter.lines[isError + 1])
	print



# Helper to print out a common error when what is recieved doesn't match the expected token
def mismatch(title, expected, received):
	print title
	print "\tExpected: " + str(expected)
	print "\tReceived: " + str(received)
	print "\t\tText: " + received.full_text()
	print


# Checks if a token matches a variable in scope
def match_variable(scope, token):
	if token.name == "VARIABLE":
		tok_name = token.full_text().strip("${}= ")

		if tok_name not in scope:
			print "Uninitialized value used:"
			print "\tValue: " + token.full_text_w_num()
			print


# Found variable name without equals sign
def report_dangling(scope, starter, token_stream):
	print "Incorrectly initialized variable:"
	print "\tToken: " + str(starter)
	print "\tVar Name: " + starter.matches[0].group(0)
	print


# Found a token without a corresponding grammar unit
def extra_token(scope, starter, token_stream):
	print "Unmatched token: "
	print "\tToken: " + str(starter)
	print "\t\tText: " + starter.matches[0].group(0)
	print


# Found a token that should be within a protocol definition
def wrong_location(scope, starter, token_stream):
	print "Token outside of protocol:"
	print "\tToken: " + str(starter)
	print



	# Token Type            Syntax Check Function (token, token_stream)
advanced_grammar = {
	"COMPOUND_NAME" : load_name,

	"FUNCTION_DEFINITION" : lambda x,y,z: search_brace(x,y,z,0),
	"ERROR_DEFINITION"    : lambda x,y,z: search_brace(x,y,z,1),

	"ASSIGN_TERMINATOR" : branch_assignment,
	"ASSIGN_SEPARATOR"  : branch_assignment,
	"ASSIGN_SYS_VAR"    : branch_assignment,
	"ASSIGN_USER_VAR"   : branch_assignment,
	"ASSIGN_EXTRA"      : branch_assignment,

	"NAME"        : report_dangling,
	"EXTRA_INPUT" : report_dangling,
	"SYS_VAR"     : report_dangling,
	"TERMINATOR"  : report_dangling,
	"SEPARATOR"   : report_dangling,

	"CONNECT"     : wrong_location,
	"DISCONNECT"  : wrong_location,
	"IN"          : wrong_location,
	"OUT"         : wrong_location,
	"EXEC"        : wrong_location,
	"EVENT"       : wrong_location,
	}


#Match a string to it's token type, returns the token type and the regex match of the string
def match(token):
	for regex, tok_name in lexicon:
		thematch = regex.match(token)

		if thematch:
			return tok_name, [thematch]

	return token, None


#Matches a list of strings to tokens, returns a list of tokens
def lexify(token_stream):
	tokens = []

	while True:
		token = token_stream.get_token()

		if not token:
			return tokens

		tok_name, tok_match = match(token)

		tokens.append(Token(tok_name, tok_match, [token_stream.lineno]))


#Does an initial pass to create complex tokens. These help us differentiate correct usage.
def grammate(token_stream):
	current_grammar = base_grammar

	#Output, list of tokens
	stack = []

	#How many matched tokens
	trail = 0

	while len(token_stream):
		token = token_stream.pop(0)

		#Matched to complex token
		if token.name in current_grammar:
			trail += 1
			current_grammar = current_grammar[token.name]

		#Doesn't have a complex form
		else:
			trail = 0
			current_grammar = base_grammar

		stack.append(token)

		#Reached the end of a complex token
		if type(current_grammar) == str:

			#Create a new token with the new name
			token_temp = Token(current_grammar, [], [])

			#Add all the component tokens
			for _ in range(trail):
				#Remove the old tokens from the stack
				token_temp.add(stack.pop(-1))

			#Place new token back into the stream
			token_stream.insert(0, token_temp)

			#Reset
			current_grammar = base_grammar
			trail = 0

	return stack


# Calls advanced grammar functions
def check_grammar(token_stream):
	scope = []

	while len(token_stream):
		token = token_stream.pop(0)

		if token.name in advanced_grammar:
			advanced_grammar[token.name](scope, token, token_stream)
		else:
			extra_token(scope, token, token_stream)


if __name__ == "__main__":
	if (sys.argv[1] == "--help" or sys.argv[1] == "-h"):
		print "validateProto.py protocol_file"
	
	else:
		with open(sys.argv[1], "r") as the_file:
			token_stream = lexify(shlex.shlex(the_file))

		check_grammar(grammate(token_stream))
