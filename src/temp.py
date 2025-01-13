import os
import jsbeautifier

def beautify_js_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        js_code = file.read()
    
    options = jsbeautifier.default_options()
    options.indent_size = 4
    options.space_in_paren = True
    
    beautified_code = jsbeautifier.beautify(js_code, options)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(beautified_code)
    print(f"文件 {file_path} 已格式化。")

def batch_beautify_js_files():
    file_path = "./ppr-jslog-nofmt.js"
    beautify_js_file(file_path)

batch_beautify_js_files()