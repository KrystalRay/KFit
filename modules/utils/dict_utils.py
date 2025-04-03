def print_unique_keys(input_dict):
    """
    打印字典中所有唯一的键
    
    Args:
        input_dict (dict): 输入的字典
    """
    unique_keys = set(input_dict.keys())
    print("Unique keys in the dictionary:")
    for key in unique_keys:
        print(f"- {key}")

if __name__ == "__main__":
    # 示例用法
    sample_dict = {
        "name": "Alice",
        "age": 30,
        "city": "New York",
        "name": "Bob",  # 重复的键会被覆盖
        "country": "USA"
    }
    print_unique_keys(sample_dict)