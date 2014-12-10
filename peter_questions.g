Questions:      (Question LineBreak*)+ 
Question:       QuestionHead Options
QuestionHead:   Numbering StringVariable Asterisk? LineBreak (explanation LineBreak)?
Options:        (RadioButtons | Checkboxes | Inputfield | List | Scale | Matrix) LineBreak

Checkboxes:     (Checkbox LineBreak)+
Checkbox:       '[' WS* ']' StringVariable 
RadioButtons:	'(' WS* ')' StringVariable

Inputfield:     Field FieldLine*
Field:          '[' Placeholder ']' Range? LineBreak
FieldLine:      '[' Underscore ]' LineBreak
Placeholder:    Underscore Text Underscore


Matrix:         Scale List

Scale:          '{' steps '}' LineBreak
steps:          step separator step (separator step)+
step:           NumberVariable

List:           '[' elements ']'
elements:       element+
element:        StringVariable LineBreak

explanation:    Text LineBreak
Numbering:      Number Period

StringVariable: Label Identifier
NumberVariable: Label Value

Label:         	Text
Identifier:    	'(' TypeConstraint? Text  ')'
NumberValue:    '(' Number ')'
Range:    		'(' Number - Number ')'

# Terminals
Text:           'a-zA-Z' + control_chars
Number:         '0-9'+
UnderScore:     '_'+
LineBreak:      '\n'
Period:         '.'
Asterisk:       '*'
WS:             ' '


# Punctuation: 	'!"$%&\'*+,-./:;<=>?@\\^`|~ '
# Text: 		a-zA-Z + 'äöüÄÖÜß'


# + : At least once
# * : None or many
# ? : One or none