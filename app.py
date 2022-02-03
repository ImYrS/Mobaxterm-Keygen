"""
    @Author: ImYrS Yang
    @Date: 2022/2/3
    @Copyright: ImYrS Yang
"""

import os
import zipfile

VariantBase64Table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
VariantBase64Dict = {i: VariantBase64Table[i] for i in range(len(VariantBase64Table))}
VariantBase64ReverseDict = {VariantBase64Table[i]: i for i in range(len(VariantBase64Table))}


def variant_base64_encode(bs: bytes):
    result = b''
    blocks_count, left_bytes = divmod(len(bs), 3)

    for i in range(blocks_count):
        coding_int = int.from_bytes(bs[3 * i:3 * i + 3], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 12) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 18) & 0x3f]
        result += block.encode()

    if left_bytes == 0:
        return result
    elif left_bytes == 1:
        coding_int = int.from_bytes(bs[3 * blocks_count:], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        result += block.encode()
        return result
    else:
        coding_int = int.from_bytes(bs[3 * blocks_count:], 'little')
        block = VariantBase64Dict[coding_int & 0x3f]
        block += VariantBase64Dict[(coding_int >> 6) & 0x3f]
        block += VariantBase64Dict[(coding_int >> 12) & 0x3f]
        result += block.encode()
        return result


def variant_base64_decode(s: str):
    result = b''
    blocks_count, left_bytes = divmod(len(s), 4)

    for i in range(blocks_count):
        block = VariantBase64ReverseDict[s[4 * i]]
        block += VariantBase64ReverseDict[s[4 * i + 1]] << 6
        block += VariantBase64ReverseDict[s[4 * i + 2]] << 12
        block += VariantBase64ReverseDict[s[4 * i + 3]] << 18
        result += block.to_bytes(3, 'little')

    if left_bytes == 0:
        return result
    elif left_bytes == 2:
        block = VariantBase64ReverseDict[s[4 * blocks_count]]
        block += VariantBase64ReverseDict[s[4 * blocks_count + 1]] << 6
        result += block.to_bytes(1, 'little')
        return result
    elif left_bytes == 3:
        block = VariantBase64ReverseDict[s[4 * blocks_count]]
        block += VariantBase64ReverseDict[s[4 * blocks_count + 1]] << 6
        block += VariantBase64ReverseDict[s[4 * blocks_count + 2]] << 12
        result += block.to_bytes(2, 'little')
        return result
    else:
        raise ValueError('Invalid encoding.')


def encrypt_bytes(key: int, bs: bytes):
    result = bytearray()
    for i in range(len(bs)):
        result.append(bs[i] ^ ((key >> 8) & 0xff))
        key = result[-1] & key | 0x482D
    return bytes(result)


def decrypt_bytes(key: int, bs: bytes):
    result = bytearray()
    for i in range(len(bs)):
        result.append(bs[i] ^ ((key >> 8) & 0xff))
        key = bs[i] & key | 0x482D
    return bytes(result)


class LicenseType:
    professional = 1
    educational = 3
    personal = 4


def generate_license(license_type: int, count: int, username: str, major_version: int, minor_version):
    assert (count >= 0)
    license_string = '%d#%s|%d%d#%d#%d3%d6%d#%d#%d#%d#' % (license_type,
                                                           username, major_version, minor_version,
                                                           count,
                                                           major_version, minor_version, minor_version,
                                                           0, 0, 0)
    encoded_license_string = variant_base64_encode(encrypt_bytes(0x787, license_string.encode())).decode()
    with zipfile.ZipFile(os.getcwd() + '/Custom.mxtpro', 'w') as f:
        f.writestr('Pro.key', data=encoded_license_string)


class Lang:
    class Zh:
        username = '请输入授权用户名: '
        version = '请输入 MobaXterm 版本号 (21.5): '
        count = '请输入授权数量 (1): '
        param_error = '参数错误'
        error = '生成错误'
        success = '生成成功, 密钥文件 "Custom.mxtpro" 已经生成到当前目录, 粘贴至 MobaXterm 程序的根目录即可.'

    class En:
        username = 'Please enter the username: '
        version = 'Please enter the MobaXterm version (21.5): '
        count = 'Please enter the license count (1): '
        param_error = 'Parameter Error'
        error = 'Error Occurred'
        success = 'Successfully Generated, the key file "Custom.mxtpro" has been generated to the current directory, ' \
                  'paste it to the root directory of MobaXterm program.'


def main():
    print('--------------------------------------------------')
    print('| MobaXterm Keygen                               |')
    print('| By ImYrS                                       |')
    print('| Version 1.0                                    |')
    print('--------------------------------------------------')

    lang = input('Language/请选择语言 (en/zh): ')
    if lang == 'zh':
        l = Lang.Zh
    elif lang == 'en':
        l = Lang.En
    else:
        print('Language error/语言错误')
        return

    username = input(l.username)
    version = input(l.version)
    count = input(l.count)

    try:
        major_version, minor_version = version.split('.')[0:2]
        count = int(count)
        major_version = int(major_version)
        minor_version = int(minor_version)
    except ValueError:
        print(l.param_error)
        return

    try:
        generate_license(LicenseType.professional, count, username, major_version, minor_version)
    except Exception as e:
        print(l.error)
        print(e)
        return
    else:
        print(l.success)


if __name__ == '__main__':
    main()
    input('\n\nProgram Completed, press ENTER to exit\n程序结束, 按 Enter 退出\n')
