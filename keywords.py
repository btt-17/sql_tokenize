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

DIMENSION = Token(r'\(\s*\b[0-9]+\b\s*\)', TTYPE.keywords)

EXACT_NUMERIC_TYPE = Token(r'NUMERIC|DECIMAL|DEC|SMALLINT|INTEGER|INT|BIGINT', TTYPE.type)

APPROX_NUMERIC_TYPE = Token(r'FLOAT|REAL|DOUBLE\s+PRECISION', TTYPE.type)

NUMERIC_TYPE = Token(str(EXACT_NUMERIC_TYPE) + r'|' + str(APPROX_NUMERIC_TYPE), TTYPE.type)


CHARACTER_STRING_TYPE = Token(r'CHAR|VARCHAR|CHARACTER', TTYPE.type)

PREDEFINED_TYPE = Token(r"(" + str(NUMERIC_TYPE)+r"|"+str(CHARACTER_STRING_TYPE) + r")" 
                        + r"\s*" + r"("+ str(DIMENSION) +r")?", TTYPE.type)

DATA_TYPE = Token(r"(" + str(PREDEFINED_TYPE)+ r")" , TTYPE.type)

DATA_TYPE_OR_DOMAIN_NAME = Token(r'('+str(DATA_TYPE)+r")", TTYPE.type)

"""
ALTER_TABLE_STATEMENT

Function: Change the definition of a table
"""
UNIQUE_SPECIFICATION = Token(r'(UNIQUE|PRIMARY\s+KEY)', TTYPE.keywords)
COLUMN_CONSTRAINT = Token(r'(NOT\s+NULL)?', TTYPE.keywords)

COLUMN_CONSTRAINT_DEFINITION = Token(str(COLUMN_CONSTRAINT), TTYPE.definition)

COLUMN_DEFINITION = Token(  str(COLUMN_NAME)  + r'\s+' + r'(' + str(DATA_TYPE_OR_DOMAIN_NAME) + r')' + 
                            r'(' + r'\s+' + str(COLUMN_CONSTRAINT_DEFINITION) + r')*', TTYPE.definition.column_definition)

DROP_BEHAVIOR = Token(r"CASCADE|RESTRICT", TTYPE.keywords)

DROP_COLUMN_DEFINITION = Token(r'(DROP(?:\b\s+COLUMN\b)?)\s+'+ r'(' + str(COLUMN_NAME)+r')' + r"(" + r"\s+" + str(DROP_BEHAVIOR) + r"\s*"  r")?" , TTYPE.definition.drop_column_definition)

ADD_COLUMN_DEFINITION = Token(r'(ADD(?:\b\s+COLUMN\b)?)\s+' + r'(' + str(COLUMN_DEFINITION) + r')' , TTYPE.definition.add_column_definition)

ALTER_TABLE_ACTION = Token(r'(' + str(ADD_COLUMN_DEFINITION)  + r'|' + str(DROP_COLUMN_DEFINITION) + r')' , TTYPE.action)

ALTER_TABLE_ACTION_LIST = [
    ADD_COLUMN_DEFINITION,
    DROP_COLUMN_DEFINITION
]

ALTER_TABLE_STATEMENT = Token(
    r'(ALTER TABLE)\s+' + r"(" 
    + str(TABLE_NAME) +r")" + r"\s+" + r"(?:" +str(ALTER_TABLE_ACTION)  + r")" + r".*", 
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
    sql_string_1 = "ALTER TABLE test ADD COLUMN `count` SMALLINT ( 6 ) NULL"
    sql_string_2 = "ALTER TABLE test ADD COLUMN `log` VARCHAR ( 12 ) NULL"
    sql_string_3 = "ALTER TABLE test ADD status INT ( 10 ) "
    sql_string_4 = "ALTER TABLE test ADD COLUMN status INT "
    sql_string_5 = "ALTER TABLE test DROP COLUMN `count`  "
    alter_table_statement_match = alter_table_statement_pattern.match(sql_string_1)

    print("(ALTER TABLE) COMMAND: ", alter_table_statement_match.group(1))
    print("(TABLE_NAME): ", alter_table_statement_match.group(2))
    print("(ALTER_TABLE_ACTION) group: ", alter_table_statement_match.group(3))

    alter_table_action_pattern = re.compile(str(ALTER_TABLE_ACTION), re.IGNORECASE)
    alter_table_action_pattern_match = alter_table_action_pattern.match(alter_table_statement_match.group(3))
    action = alter_table_action_pattern_match.group(1)
    for action_regex in ALTER_TABLE_ACTION_LIST:
            action_pattern = re.compile(str(action_regex), re.IGNORECASE)
            action_match = action_pattern.match(action)
            
            if not action_match:
                continue

            if action_regex.type == TTYPE.definition.drop_column_definition:
                print("(DROP COLUMN): ", action_match.group(1))
                print("(COLUMN NAME): ", action_match.group(2))

            if action_regex.type == TTYPE.definition.add_column_definition:
                print("(ADD COLUMN) COMMAND: ", action_match.group(1))
                print("(COLUMN DEFINITION): ", action_match.group(2))

                column_definition_pattern = re.compile(str(COLUMN_DEFINITION), re.IGNORECASE)
                column_definition_match = column_definition_pattern.match(action_match.group(2))
                print("(COLUMN NAME): ", column_definition_match.group(1))
                print("(DATA TYPE OR DOMAIN_NAME): ", column_definition_match.group(2))

                data_type_or_domain_pattern = re.compile(str(DATA_TYPE_OR_DOMAIN_NAME), re.IGNORECASE)
                data_type_or_domain_match = data_type_or_domain_pattern.match(column_definition_match.group(2))
                print("(DATA TYPE): ", data_type_or_domain_match.group(1))
            
                data_type_pattern =re.compile(str(DATA_TYPE), re.IGNORECASE)
                data_type_match = data_type_pattern.match(data_type_or_domain_match.group(1))
                print("(PREDEFINED DATA): ", data_type_match.group(1))

                predifined_data_type_pattern = re.compile(str(PREDEFINED_TYPE), re.IGNORECASE)
                predifined_data_type_match = predifined_data_type_pattern.match(data_type_match.group(1))
                print("(NUMERIC OR CHAR): ", predifined_data_type_match.group(1))
                print("(DIMENSION): ", predifined_data_type_match.group(2))
    

def test_alter_table_multi_action():
    alter_table_statement_pattern = re.compile(str(ALTER_TABLE_STATEMENT), re.IGNORECASE)
    sql_string = "ALTER TABLE test ADD COLUMN `count` SMALLINT ( 10 ) , ADD COLUMN `log` VARCHAR ( 12 ) , ADD COLUMN status INT ( 10 ) , DROP COLUMN `count`  "
    alter_table_statement_match = alter_table_statement_pattern.match(sql_string+" ,")
    print("(ALTER TABLE) COMMAND: ", alter_table_statement_match.group(1))
    print("(TABLE_NAME): ", alter_table_statement_match.group(2))

    actions_list = []
    actions_list.append(alter_table_statement_match.group(3))
    actions_list.extend(sql_string.split(',')[1:])

    for i, action in enumerate(actions_list):
        print(f"===== Action {i+1} ====")
        action = action.strip()
        print("Line 141: ", action)

        for action_regex in ALTER_TABLE_ACTION_LIST:
            action_pattern = re.compile(str(action_regex), re.IGNORECASE)
            action_match = action_pattern.match(action)
            
            if not action_match:
                continue

            if action_regex.type == TTYPE.definition.drop_column_definition:
                print("(DROP COLUMN): ", action_match.group(1))
                print("(COLUMN NAME): ", action_match.group(2))

            if action_regex.type == TTYPE.definition.add_column_definition:
                print("(ADD COLUMN) COMMAND: ", action_match.group(1))
                print("(COLUMN DEFINITION): ", action_match.group(2))

                column_definition_pattern = re.compile(str(COLUMN_DEFINITION), re.IGNORECASE)
                column_definition_match = column_definition_pattern.match(action_match.group(2))
                print("(COLUMN NAME): ", column_definition_match.group(1))
                print("(DATA TYPE OR DOMAIN_NAME): ", column_definition_match.group(2))

                data_type_or_domain_pattern = re.compile(str(DATA_TYPE_OR_DOMAIN_NAME), re.IGNORECASE)
                data_type_or_domain_match = data_type_or_domain_pattern.match(column_definition_match.group(2))
                print("(DATA TYPE): ", data_type_or_domain_match.group(1))
            
                data_type_pattern =re.compile(str(DATA_TYPE), re.IGNORECASE)
                data_type_match = data_type_pattern.match(data_type_or_domain_match.group(1))
                print("(PREDEFINED DATA): ", data_type_match.group(1))

                predifined_data_type_pattern = re.compile(str(PREDEFINED_TYPE), re.IGNORECASE)
                predifined_data_type_match = predifined_data_type_pattern.match(data_type_match.group(1))
                print("(NUMERIC OR CHAR): ", predifined_data_type_match.group(1))
                print("(DIMENSION): ", predifined_data_type_match.group(2))
        
# Main function
if __name__=="__main__":
#    test_alter_table_single_action()
   test_alter_table_multi_action()


    


