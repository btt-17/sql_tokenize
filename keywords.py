"""
References:
[1] https://learn.microsoft.com/en-us/sql/relational-databases/databases/database-identifiers?view=sql-server-ver16
[2] https://github.com/andialbrecht/sqlparse
[3] https://github.com/ronsavage/SQL/blob/master/sql-2016.ebnf
"""

import re 
from token import Token, TokenType
TTYPE = TokenType()

"""
    SQL comment
"""
SINGLE_COMMENT = Token(r'\s*(--).*?(\r\n|\r|\n|$)', TTYPE.comment)

BRACKETED_COMMENT = Token(r'\s*/\*[\s\S]*?\*/', TTYPE.comment)

COMMENT = Token(r"(" + str(SINGLE_COMMENT) + r")" + r"|" + r"(" + str(BRACKETED_COMMENT) + r")", TTYPE.comment)

"""
    Special Character
"""
L_PAREN = Token(r'[\b(\b]', TTYPE.special_character)

R_PAREN = Token(r'[\b)\b]', TTYPE.special_character)

COMMA = Token(r'[\b,\b]',  TTYPE.special_character)

WHITE_SPACE = Token(r'\s', TTYPE.special_character)

"""
    regex for cleaning and normalizing sql statements
"""
CLEAN = [
    (COMMENT, ""),
    (COMMA, " , "),
    (L_PAREN, " ( "),
    (R_PAREN, " ) "),
    (WHITE_SPACE+r'{2,}', " "),
]

IDENTIFIER = Token(r'[\w_][\w\d}@$#_]{0,127}', TTYPE.identifier)

TABLE_NAME = Token(str(IDENTIFIER), TTYPE.identifier)

COLUMN_NAME =  Token(r"(`?\b"+str(IDENTIFIER)+r"\b`?)", TTYPE.identifier)


"""
    Data Type
"""
EXACT_NUMERIC_TYPE = Token(r'(NUMERIC|DECIMAL|DEC|SMALLINT|INTEGER|INT|BIGINT)', TTYPE.type)

APPROX_NUMERIC_TYPE = Token(r'(FLOAT|REAL|DOUBLE\s+PRECISION)', TTYPE.type)

NUMERIC_TYPE = Token(r'(' + str(EXACT_NUMERIC_TYPE) + r'|' + str(APPROX_NUMERIC_TYPE)+r')', TTYPE.type)


CHARACTER_STRING_TYPE = Token(r'(CHAR|VARCHAR|CHARACTER)', TTYPE.type)

PREDEFINED_TYPE = Token(str(NUMERIC_TYPE)+r"|"+str(CHARACTER_STRING_TYPE), TTYPE.type)

DATA_TYPE = Token(r'('+str(PREDEFINED_TYPE)+r")", TTYPE.type)

DATA_TYPE_OR_DOMAIN_NAME = Token(r'('+str(DATA_TYPE)+r")", TTYPE.type)

"""
ALTER_TABLE_STATEMENT

Function: Change the definition of a table
"""

COLUMN_DEFINITION = Token(  str(COLUMN_NAME)  + r'\s+' + r'(' + str(DATA_TYPE_OR_DOMAIN_NAME) + r')', TTYPE.definition)

ADD_COLUMN_DEFINITION = Token(r'(ADD\s+(?:\bCOLUMN\b)?)\s+' +r'(' + str(COLUMN_DEFINITION) + r')' , TTYPE.definition)

ALTER_TABLE_ACTION = Token(r'(' + str(ADD_COLUMN_DEFINITION)  + r')'  , TTYPE.action)

ALTER_TABLE_STATEMENT = Token(
    r'(ALTER TABLE)\s+' + r"(" 
    + str(TABLE_NAME) +r")" + r"\s+" + r"(?:" +str(ALTER_TABLE_ACTION)  + r"){1,}" + r".*", 
    TTYPE.statement.alter_table
)


"""
    SQL statements
"""

STATEMENTS = [
    ALTER_TABLE_STATEMENT,
]

def test_alter_table_single_action():
    alter_table_statement_pattern = re.compile(str(ALTER_TABLE_STATEMENT), re.IGNORECASE)
    sql_string = "ALTER TABLE test ADD COLUMN `count` SMALLINT ( 6 ) NULL"

    regex_match = alter_table_statement_pattern.match(sql_string)

    print("(ALTER TABLE) COMMAND: ", regex_match.group(1))
    print("(TABLE_NAME): ", regex_match.group(2))
    print("(ALTER_TABLE_ACTION) group: ", regex_match.group(3))
  
    alter_table_action_pattern = re.compile(str(ALTER_TABLE_ACTION), re.IGNORECASE)
    regex_match_2 = alter_table_action_pattern.match(regex_match.group(3))
 
    print("(ADD COLUMN DEFINITION): ", regex_match_2.group(1))

    add_column_definition_pattern = re.compile(str(ADD_COLUMN_DEFINITION), re.IGNORECASE)
    regex_match_3 = add_column_definition_pattern.match(regex_match_2.group(1))
    print("(ADD COLUMN) COMMAND: ", regex_match_3.group(1))
    print("(COLUMN DEFINITION): ", regex_match_3.group(2))

    column_definition_pattern = re.compile(str(COLUMN_DEFINITION), re.IGNORECASE)
    regex_match_4 = column_definition_pattern.match(regex_match_3.group(2))
    print("(COLUMN NAME): ", regex_match_4.group(1))
    print("(DATA TYPE OR DOMAIN_NAME): ", regex_match_4.group(2))

def test_alter_table_multi_action():
    alter_table_statement_pattern = re.compile(str(ALTER_TABLE_STATEMENT), re.IGNORECASE)
    sql_string = "ALTER TABLE test ADD COLUMN `count` SMALLINT  , ADD COLUMN `log` VARCHAR  , ADD COLUMN status INT "
    regex_match = alter_table_statement_pattern.match(sql_string+" ,")
    print("(ALTER TABLE) COMMAND: ", regex_match.group(1))
    print("(TABLE_NAME): ", regex_match.group(2))

    
    actions_list = []
    actions_list.append(regex_match.group(3))
    actions_list.extend(sql_string.split(',')[1:])

    for i, action in enumerate(actions_list):
        print(f"===== Action {i+1} ====")
        action = action.strip()
        alter_table_action_pattern = re.compile(str(ALTER_TABLE_ACTION), re.IGNORECASE)
        regex_match_2 = alter_table_action_pattern.match(action)
    
        print("(ADD COLUMN DEFINITION): ", regex_match_2.group(1))

        add_column_definition_pattern = re.compile(str(ADD_COLUMN_DEFINITION), re.IGNORECASE)
        regex_match_3 = add_column_definition_pattern.match(regex_match_2.group(1))
        print("(ADD COLUMN) COMMAND: ", regex_match_3.group(1))
        print("(COLUMN DEFINITION): ", regex_match_3.group(2))

        column_definition_pattern = re.compile(str(COLUMN_DEFINITION), re.IGNORECASE)
        regex_match_4 = column_definition_pattern.match(regex_match_3.group(2))
        print("(COLUMN NAME): ", regex_match_4.group(1))
        print("(DATA TYPE OR DOMAIN_NAME): ", regex_match_4.group(2))


# Main function
if __name__=="__main__":
#    test_alter_table_single_action()
   test_alter_table_multi_action()


    


