"""
Coze文档清洗与结构化工具
功能包含：跨文件去重、术语标准化、代码规范化、知识库生成
"""

import re
import hashlib
from pathlib import Path
from collections import defaultdict

# 配置参数
TERM_MAPPING = {
    "Bot": "智能体",
    "卡片": "交互组件",
    "参数": "输入参数",
    "NL2SQL": "自然语言转SQL"
}

SECTION_PATTERN = re.compile(r'\n##+\s+(.*?)\n')
CODE_BLOCK_PATTERN = re.compile(r'```python\n(.*?)```', re.DOTALL)

class CozeDocCleaner:
    def __init__(self, input_dir="coze_docs", output_dir="knowledge_base"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.known_sections = defaultdict(set)  # 用于跨文件去重
        
    def process_all(self):
        """处理目录下所有txt文档"""
        for txt_file in self.input_dir.glob("*.txt"):
            print(f"Processing {txt_file.name}...")
            content = txt_file.read_text(encoding='utf-8')
            cleaned = self.clean_content(content)
            self.generate_knowledge_files(cleaned, txt_file.stem)

    def clean_content(self, text: str) -> dict:
        """主清洗流程"""
        # 阶段1：结构化处理
        sections = self._split_sections(text)
        
        # 阶段2：内容清洗
        processed = {}
        for title, content in sections:
            # 跨文件去重
            content_hash = self._content_hash(content)
            if content_hash in self.known_sections[title]:
                continue
                
            # 术语替换
            cleaned = self._replace_terms(content)
            
            # 代码块规范化
            cleaned = self._format_code_blocks(cleaned)
            
            processed[title] = cleaned
            self.known_sections[title].add(content_hash)
        
        return processed

    def _split_sections(self, text: str) -> list:
        """按标题切分章节"""
        sections = []
        last_pos = 0
        
        for match in SECTION_PATTERN.finditer(text):
            title = match.group(1).strip()
            start = match.start()
            if start > last_pos:
                content = text[last_pos:start]
                sections.append(("前置内容", content))
            sections.append((title, ""))
            last_pos = match.end()
        
        if last_pos < len(text):
            sections.append(("其他内容", text[last_pos:]))
            
        return sections

    def _replace_terms(self, text: str) -> str:
        """术语统一替换"""
        for old, new in TERM_MAPPING.items():
            text = re.sub(rf'\b{old}\b', new, text)
        return text

    def _format_code_blocks(self, text: str) -> str:
        """代码块格式化"""
        def _code_formatter(match):
            code = match.group(1)
            # 统一缩进为4空格
            code = '\n'.join(line.rstrip() for line in code.split('\n'))
            return f"```python\n{code}\n```"
            
        return CODE_BLOCK_PATTERN.sub(_code_formatter, text)

    def _content_hash(self, text: str) -> str:
        """生成内容指纹"""
        return hashlib.md5(text.encode()).hexdigest()

    def generate_knowledge_files(self, data: dict, source: str):
        """生成结构化知识库"""
        # 创建目录结构
        (self.output_dir/"workflow_types").mkdir(exist_ok=True, parents=True)
        (self.output_dir/"node_config").mkdir(exist_ok=True)
        
        # 按内容类型处理
        for title, content in data.items():
            if "工作流" in title:
                self._save_workflow(content, title, source)
            elif "节点" in title:
                self._save_node_config(content, title, source)
                

def _save_workflow(self, content: str, title: str, source: str):
    """保存工作流文档"""
    safe_title = self.sanitize_filename(title)  # 新增清洗步骤
    filename = f"{safe_title}.md"
    workflow_dir = self.output_dir/"workflow_types"
    workflow_dir.mkdir(exist_ok=True, parents=True)  # 确保目录存在
    
    path = workflow_dir / filename
    # ...后续代码保持不变...def _remove_junk_sections(self, text: str) -> str:
    """移除无用章节（版本历史、变更记录等）"""
    junk_patterns = [
        r'## 版本历史.*?(\n## |$)', 
        r'## 变更记录.*?(\n## |$)',
        r'<!-- deprecated -->.*?-->'
    ]
    for pattern in junk_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
    return text
path = (self.output_dir
        .joinpath("node_config")
        .joinpath(filename))
    def process_all(self):
        # ...原有处理逻辑...
        self._validate_cleaning(txt_file, cleaned)  # 新增验证步骤

    def _validate_cleaning(self, original_file, cleaned_data):
        """清洗质量检查"""
        error_log = []
        for title, content in cleaned_data.items():
            # 检查术语替换
            if any(old in content for old in TERM_MAPPING):
                error_log.append(f"{title}存在未替换术语")
            
            # 检查代码块完整性
            code_blocks = CODE_BLOCK_PATTERN.findall(content)
            if code_blocks and not any('```python' in content for _ in code_blocks):
                error_log.append(f"{title}代码块格式异常")
        
        if error_log:
            log_file = self.output_dir / f"error_{original_file.stem}.log"
            log_file.write_text('\n'.join(error_log))

    def _save_node_config(self, content: str, title: str, source: str):
        """保存节点配置"""
        filename = title.replace(" ", "_") + ".md"
        path = self.output_dir/"node_config"/filename
        
        # 提取代码示例
        codes = CODE_BLOCK_PATTERN.findall(content)
        table = "## 代码示例\n\n" + self._generate_code_table(codes)
        
        full_content = f"# {title}\n**来源**: {source}\n\n{table}\n\n{content}"
        path.write_text(full_content, encoding='utf-8')

    def _generate_code_table(self, codes: list) -> str:
        """生成代码示例表格"""
        if not codes:
            return ""
            
        table = ["| 示例 | 描述 |", "|------|-----|"]
        for i, code in enumerate(codes, 1):
            desc = self._parse_code_comment(code) or "代码示例"
            table.append(f"| 示例{i} | {desc} |")
        return '\n'.join(table)

    def _parse_code_comment(self, code: str) -> str:
        """解析代码首行注释"""
        first_line = code.split('\n')[0].strip()
        if first_line.startswith('#'):
            return first_line[1:].strip()
        return ""

if __name__ == "__main__":
    cleaner = CozeDocCleaner(input_dir="coze_docs", output_dir="knowledge_base")
    cleaner.process_all()
    print("文档清洗与结构化完成！")
    # 新增文件名清洗方法
def sanitize_filename(self, name: str) -> str:
    """确保文件名符合系统规范"""
    # 替换Windows系统非法字符为下划线
    illegal_chars = r'[\\/*?:"<>|]'
    return re.sub(illegal_chars, '_', name).strip()

# 修改后的保存节点配置方法
def _save_node_config(self, content: str, title: str, source: str):
    """保存节点配置"""
    # 新增文件名清洗步骤
    safe_title = self.sanitize_filename(title)
    filename = f"{safe_title}.md"  # 移除了原来的replace空格操作
    
    # 确保目录存在（新增）
    config_dir = self.output_dir/"node_config"
    config_dir.mkdir(exist_ok=True, parents=True)
    
    path = config_dir / filename
    
    # 提取代码示例（保持不变）
    codes = CODE_BLOCK_PATTERN.findall(content)
    table = "## 代码示例\n\n" + self._generate_code_table(codes)
    
    # 内容生成（保持不变）
    full_content = f"# {title}\n**来源**: {source}\n\n{table}\n\n{content}"
    
    try:
        path.write_text(full_content, encoding='utf-8')
    except Exception as e:
        print(f"保存文件失败: {path}\n错误信息: {str(e)}")