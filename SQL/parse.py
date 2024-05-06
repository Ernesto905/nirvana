import re

def extract_sql(response):
    sql_pattern = r"```sql\n(.*?)```"
    sql_match = re.search(sql_pattern, response, re.DOTALL)
    
    if sql_match:
        sql_code = sql_match.group(1)
        cleaned_sql = sql_code.replace('\n', ' ').strip()
        return cleaned_sql
    else:
        # Return None if no SQL code is found
        return None

