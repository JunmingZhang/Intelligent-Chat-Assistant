from dynamo import DynamoDBConn
import time

if __name__ == "__main__":
    db_conn = DynamoDBConn()
    print(db_conn.client.list_tables()['TableNames'])
    db_conn.create_signup_table()
    print(db_conn.client.list_tables()['TableNames'])

    response = db_conn.userinfo_put_item('abc@drf.com', 'peter', 'abc')
    print(response)
    print(db_conn.userinfo_query('abc@drf.com', 'abc'))
    print(db_conn.userinfo_query('a@drf.com', 'abc'))
    print(db_conn.userinfo_query('abc@drf.com', 'acc'))
    db_conn.userinfo_put_item('abc@def.com', 'andy', 'cdf')
    print(db_conn.get_num_users())
    db_conn._user_delete('abc@drf.com', 'peter')
    db_conn._user_delete('abc@def.com', 'andy')

    print(db_conn.client.list_tables()['TableNames'])
    db_conn.create_chatlog_table()
    print(db_conn.client.list_tables()['TableNames'])

    response = db_conn.userlog_put_item('abc@drf.com', 'peter')
    print(db_conn.userlog_query('abc@drf.com', 'peter'))
    time.sleep(5)
    response = db_conn.update_userlog_last_action_time('abc@drf.com', 'peter')
    print(response)
    print(db_conn.userlog_query('abc@drf.com', 'peter'))
    db_conn._chatlog_delete('abc@drf.com', 'peter')

    # db_conn._delete_signup_table()
    # db_conn._delete_chatlog_table()