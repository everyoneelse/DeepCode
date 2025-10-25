# Cursor Agentic Coding Prompts

这个目录包含了将DeepCode仓库的功能转化为Cursor编辑器可用的prompt集合。通过这些prompt，您可以直接与Cursor交互完成原本需要复杂MCP系统才能实现的agentic-coding功能。

## 目录结构

```
cursor_prompts/
├── README.md                    # 本文件
├── core_prompts/               # 核心功能prompt
│   ├── paper_analysis.md       # 论文分析prompt
│   ├── code_planning.md        # 代码规划prompt
│   ├── code_implementation.md  # 代码实现prompt
│   └── project_setup.md        # 项目设置prompt
├── workflow_guides/            # 工作流指南
│   ├── paper_to_code.md        # 论文转代码工作流
│   ├── requirements_to_code.md # 需求转代码工作流
│   └── best_practices.md       # 最佳实践
└── examples/                   # 使用示例
    ├── example_paper.md        # 示例论文
    ├── example_requirements.md # 示例需求
    └── example_outputs/        # 示例输出
```

## 快速开始

1. **论文转代码**：使用 `core_prompts/paper_analysis.md` 分析论文，然后使用 `core_prompts/code_planning.md` 生成实现计划
2. **需求转代码**：直接使用 `core_prompts/code_planning.md` 从文本需求生成代码计划
3. **代码实现**：使用 `core_prompts/code_implementation.md` 将计划转换为实际代码

## 主要优势

- **无需复杂环境配置**：直接在Cursor中使用，无需安装MCP服务器
- **交互式开发**：可以与Cursor进行多轮对话，逐步完善代码
- **灵活定制**：可以根据具体需求调整prompt
- **即时反馈**：实时查看代码生成结果并进行调整

## 使用方法

1. 复制相应的prompt到Cursor
2. 根据提示提供输入（论文、需求等）
3. 让Cursor分析并生成代码
4. 根据需要进行迭代改进

详细的使用指南请查看 `workflow_guides/` 目录下的文档。