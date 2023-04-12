from sql_util import sql_token
if __name__=="__main__":
    # statement="""
    # /* debug */

    # --Test:
    #     ALTER TABLE test
    #     ADD COLUMN `count` SMALLINT(6) NULL ,
    #     ADD COLUMN `log` VARCHAR(12) NULL default 'blah' AFTER `count`,
    #     ADD COLUMN new_enum ENUM('asd','r') NULL AFTER `log`,
    #     ADD COLUMN status /*debug*/ INT(10) UNSIGNED NULL AFTER `new_enum`
    # """
    statement="""
    /* debug */

    --Test:
        ALTER TABLE test
        ADD COLUMN `count` SMALLINT(6) NULL,
        ADD COLUMN `log` VARCHAR(12),
        ADD status /*debug*/ INT(10),
        DROP COLUMN `count`,
        DROP FOREIGN KEY fk_trigger_bar
    """
    token_sql=sql_token()
    token_sql.parse_sql(statement)
    print(token_sql.tokenised)