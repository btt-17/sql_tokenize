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
        for action in actions_list:
            cmd = {}
          
            action = action.strip()
            alter_table_action_pattern = re.compile(str(keywords.ALTER_TABLE_ACTION), re.IGNORECASE)
            alter_table_action_match = alter_table_action_pattern.match(action)
          
            add_column_definition_pattern = re.compile(str(keywords.ADD_COLUMN_DEFINITION), re.IGNORECASE)
            add_column_definition_match = add_column_definition_pattern.match(alter_table_action_match.group(1)) 

            cmd['command'] = add_column_definition_match.group(1).strip()
           
            column_definition_pattern = re.compile(str(keywords.COLUMN_DEFINITION), re.IGNORECASE)
            column_definition_match = column_definition_pattern.match(add_column_definition_match.group(2))
        
            cmd['name'] = column_definition_match.group(1).strip().strip("`")
            cmd['column_type'] = column_definition_match.group(2).strip().lower().replace(" ", "")

            data_type_or_domain_pattern = re.compile(str(keywords.DATA_TYPE_OR_DOMAIN_NAME), re.IGNORECASE)
            data_type_or_domain_match = data_type_or_domain_pattern.match(column_definition_match.group(2))
        
            data_type_pattern =re.compile(str(keywords.DATA_TYPE), re.IGNORECASE)
            data_type_match = data_type_pattern.match(data_type_or_domain_match.group(1))

            predifined_data_type_pattern = re.compile(str(keywords.PREDEFINED_TYPE), re.IGNORECASE)
            predifined_data_type_match = predifined_data_type_pattern.match(data_type_match.group(1))
            cmd['data_type'] = predifined_data_type_match.group(1).lower().strip()
            dimension = predifined_data_type_match.group(2).lower()
            dimension = dimension.replace("(","")
            dimension = dimension.replace(")","")
            dimension = dimension.strip()
            cmd['dimension'] = dimension
            alter_cmd.append(cmd)

        stat_dict['alter_cmd'] = alter_cmd
        return stat_dict
