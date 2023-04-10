import re
import token 
import keywords

class sql_token(object):
    def __init__(self):
        self.tokenised = []
        self.clear()
        self.set_STATEMENTS_REGEX(keywords.STATEMENTS) #default
    
    def clear(self):
        self._SQL_STATEMENT = []
        
    def set_STATEMENTS_REGEX(self, RULES):
        self._SQL_STATEMENT = [
            (re.compile(str(statement_regex), re.IGNORECASE).match, statement_regex.type)
            for statement_regex in RULES
        ]

    def clean(self, statement):
        for clean_token, new_token in keywords.CLEAN:
            statement = re.sub(str(clean_token), new_token, statement)
        statement = statement.replace("\n", "")
        statement = statement.strip()
        return statement
    
    
    def parse_sql(self, sql_statements):
        statements_list = sql_statements.split(';')
        for statement in statements_list:
            stat_dict = {}
            stat_cleanup = self.clean(statement)
            
            for cmd_regex_match, cmd_type in self._SQL_STATEMENT:
                match_result = cmd_regex_match(stat_cleanup)
                
                if not match_result:
                    continue
                else:
                    if cmd_type == keywords.TTYPE.statement.alter_table:
                       
                        stat_dict = self.parse_alter_table(match_result)
                        break


            if len(stat_dict) != 0:
                self.tokenised.append(stat_dict)

    def parse_alter_table(self, regex_match):
        stat_dict = {}
        alter_stat = regex_match.group(0)
        stat_dict ["command"] = regex_match.group(1).upper().strip()
        stat_dict ["name"] = regex_match.group(2).strip().strip('`')

        actions_list = []
        actions_list.append(regex_match.group(3))
        actions_list.extend(alter_stat.split(',')[1:])
        alter_cmd = []
        for i, action in enumerate(actions_list):
            cmd = {}
          
            action = action.strip()
            alter_table_action_pattern = re.compile(str(keywords.ALTER_TABLE_ACTION), re.IGNORECASE)
            regex_match_2 = alter_table_action_pattern.match(action)
        
            # print("(ADD COLUMN DEFINITION): ", regex_match_2.group(1))
        
            add_column_definition_pattern = re.compile(str(keywords.ADD_COLUMN_DEFINITION), re.IGNORECASE)
            regex_match_3 = add_column_definition_pattern.match(regex_match_2.group(1))
     

            cmd['command'] = regex_match_3.group(1)

            column_definition_pattern = re.compile(str(keywords.COLUMN_DEFINITION), re.IGNORECASE)
            regex_match_4 = column_definition_pattern.match(regex_match_3.group(2))
            # print("(COLUMN NAME): ", regex_match_4.group(1))
            # print("(DATA TYPE OR DOMAIN_NAME): ", regex_match_4.group(2))
            cmd['name'] = regex_match_4.group(1)
            cmd['type'] = regex_match_4.group(2)
            alter_cmd.append(cmd)
        stat_dict['alter_cmd'] = alter_cmd
        return stat_dict
