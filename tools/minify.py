import re
import sys
import os

def minify_css(css):
    # Remove comments
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
    # Remove whitespace
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([:;{}])\s*', r'\1', css)
    return css

def minify_js(js):
    # Very basic JS minification
    lines = js.split('\n')
    minified_lines = []
    for line in lines:
        line = line.strip()
        # removing full line comments
        if line.startswith('//'):
            continue
        if line:
            minified_lines.append(line)
    return '\n'.join(minified_lines)

def minify_html(content):
    # Remove HTML comments
    content = re.sub(r'<!--(.*?)-->', '', content, flags=re.DOTALL)
    
    # Minify CSS style blocks
    def replace_css(match):
        return f'<style>{minify_css(match.group(1))}</style>'
    content = re.sub(r'<style>(.*?)</style>', replace_css, content, flags=re.DOTALL)

    # Minify JS script blocks (Conservative)
    # definition of conservative: don't join lines, just trim
    def replace_js(match):
         return f'<script>{" ".join([l.strip() for l in match.group(1).splitlines() if l.strip()])}</script>'
    
    # We will use a safer approach for the whole file:
    # 1. Remove whitespace between tags
    content = re.sub(r'>\s+<', '><', content)
    
    # 2. Collapse multiple spaces in text (be careful with pre/code, but here it's fine)
    # content = re.sub(r'\s+', ' ', content) # This is too aggressive for JS/CSS if not carefully isolated
    
    return content

def main():
    # Adjust paths relative to the script location or current working directory
    # Assuming script is run from project root
    input_path = 'main/homepage_full.html'
    output_path = 'main/homepage.html'
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        sys.exit(1)

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. Minify CSS
        content = re.sub(r'<style>(.*?)</style>', lambda m: f'<style>{minify_css(m.group(1))}</style>', content, flags=re.DOTALL)
        
        # 2. Remove HTML comments
        content = re.sub(r'<!--(.*?)-->', '', content, flags=re.DOTALL)
        
        # 3. Collapse whitespace between tags
        content = re.sub(r'>\s+<', '><', content)
        
        # 4. Trim lines and remove empty lines
        lines = content.split('\n')
        # Simple line trimming
        content = "".join([line.strip() for line in lines])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Successfully minified {input_path} to {output_path}")
        print(f"Original size: {os.path.getsize(input_path)} bytes")
        print(f"Minified size: {os.path.getsize(output_path)} bytes")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
