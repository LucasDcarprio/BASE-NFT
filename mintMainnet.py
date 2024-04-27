from web3 import Web3,Account
import requests,json
import random,time
rpc = ["https://developer-access-mainnet.base.org","https://mainnet.base.org","https://base.llamarpc.com","https://base.blockpi.network/v1/rpc/public","https://1rpc.io/base","https://base-pokt.nodies.app","https://base.meowrpc.com","https://base-mainnet.public.blastapi.io","https://base.gateway.tenderly.co","https://gateway.tenderly.co/public/base","https://base.drpc.org","https://endpoints.omniatech.io/v1/base/mainnet/public","https://base.api.onfinality.io/public","https://public.stackup.sh/api/v1/node/base-mainnet","https://api.tatum.io/v3/blockchain/node/base-mainnet","https://base.rpc.subquery.network/public","https://gateway.subquery.network/rpc/base"]
def getResult(address):
#设置代理，替换为你的代理地址和端口
    proxies = {
        "http": "http://your_proxy_address:proxy_port",
        "https": "https://your_proxy_address:proxy_port",
    }

    # 设置请求头，只保留了可能必需的部分
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    # 请求载荷
    payload = {
        "address": address
    }

    # 发起请求
    url = 'https://www.base.org/api/checkNftProof'
    response = requests.post(url, json=payload, headers=headers, proxies=None)
    print(response)
    if response.status_code == 200:
        response=json.loads(response.text)
        # 输出响应
        # print(response)
        # 假设的函数选择器
        function_selector = "0xb77a147b"
        # 示例结果数组
        result = response['result']
        return function_selector, result
    else:
        print('没有资格')
        return None,None
# 编码逻辑
def encode_signature(function_selector, result):
    # 数据偏移量（数组开始位置），因为仅有数组一个动态参数，所以固定为32字节（0x20）
    offset = 32

    # 数组长度，转换为十六进制
    length_hex = Web3.to_hex(len(result))

    # 合并结果数组的数据，去掉每个元素的 '0x'
    result_data = ''.join(item[2:] for item in result)

    # 构建完整的数据字符串
    # 动态类型数据编码格式：偏移量（十六进制表示）+ 数据长度（十六进制表示）+ 实际数据
    signature = (
        function_selector +
        Web3.to_hex(offset)[2:].zfill(64) +
        length_hex[2:].zfill(64) +
        result_data
    )

    return signature

def mint(rpc,key,data):
        w3 = Web3(Web3.HTTPProvider(random.choice(rpc)))
        address=Account.from_key(key).address
        # 构建交易参数后直接发送
        transaction = {
            'from':  w3.to_checksum_address(address),
            'value': 0,
            'gas': 150000,
            'nonce': w3.eth.get_transaction_count(address),
            'data': data,
            'to': w3.to_checksum_address('0x8dc80a209a3362f0586e6c116973bb6908170c84'),
            'gasPrice': w3.to_wei(0.2, 'gwei'),
            "chainId": w3.eth.chain_id,
        }

        # 签名
        signed_txn = w3.eth.account.sign_transaction(transaction, key)
        # 发送
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print('MINT已发送，哈希为：', tx_hash.hex())
        # 等待交易被打包上链
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print('MINT成功，交易回执为：', receipt['transactionHash'].hex())
        with open('mintLog.txt','a+',encoding='utf-8') as fm:
                fm.write(address+'成功mint，哈希->'+str(receipt['transactionHash'].hex())+f'\n')
# 使用函数
with open('私钥.txt','r',encoding='utf-8') as f :
    fs = f.readlines()

with open('地址.txt','w+',encoding='utf-8') as fw :
    for i in range(len(fs)):
        key=(fs[i].strip('\n'))
        fw.write(Account.from_key(key).address)
        fw.write(f'\n')
for i in range(len(fs)):
    try:
        key=(fs[i].strip('\n'))
        function_selector, result = getResult(address=Account.from_key(key).address)
        if function_selector:
            encoded_signature = encode_signature(function_selector, result)
            if encoded_signature:
                mint(rpc,key,encoded_signature)
    except Exception as e :
        print('出现错误：')
        print(e)
        # print(encoded_signature)
