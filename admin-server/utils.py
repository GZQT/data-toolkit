from datetime import datetime


def get_substring_before_keyword(full_string, keyword):
    # 使用split方法切割字符串
    parts = full_string.split(keyword)
    if len(parts) > 1:
        return parts[0]
    else:
        # 如果keyword不在字符串中，返回原字符串
        return full_string


def get_now_date():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
