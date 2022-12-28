from s3 import S3Conn

if __name__ == "__main__":
    s3_conn = S3Conn()
    print(s3_conn.s3.Bucket(s3_conn.bucket_name) in s3_conn.s3.buckets.all())
    res = s3_conn.create_bucket()
    print(res)
    print(s3_conn.s3.Bucket(s3_conn.bucket_name) in s3_conn.s3.buckets.all())
    s3_conn.upload_avatar('./app/static/test_images/3.jpeg', 'peter@abc.com')
    s3_conn.upload_chatlog('peter@abc.com')
    s3_conn.upload_chatlog('peter@abc.com', 'hello world!')
    s3_conn.upload_chatlog('peter@abc.com', 'how are you?\nI am okay.')
    s3_conn.download_chatlog('peter@abc.com', './app/static/userfiles/peter@abc.com/chatlog.txt')
    s3_conn.download_avatar('peter@abc.com', './app/static/userfiles/peter@abc.com/avatar.png')

    # s3_conn.delete_folder('peter@abc.com')
    # s3_conn.delete_avatar('peter@abc.com')
    # s3_conn.delete_chatlog('peter@abc.com')