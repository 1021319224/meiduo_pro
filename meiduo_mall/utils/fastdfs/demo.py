from fdfs_client.client import Fdfs_client

client = Fdfs_client('/home/python/Desktop/meiduo_pro/meiduo_mall/utils/fastdfs/client.conf')

ret = client.upload_by_filename('/home/python/Desktop/meiduo_pro/meiduo_mall/utils/fastdfs/adv01.jpg')

# print(client)