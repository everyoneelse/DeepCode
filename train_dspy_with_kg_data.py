#!/usr/bin/env python3
"""
使用你的知识图谱数据训练DSPy模型
实战示例：属性去重任务
"""

import json
import dspy
from typing import List, Dict
from dspy.teleprompt import BootstrapFewShot


# ==================== 步骤1: 定义DSPy签名 ====================

class AttributeDedup(dspy.Signature):
    """
    属性去重任务签名
    目标: 从多个可能重复的属性描述中，选出最准确、最完整的属性
    """
    entity_name: str = dspy.InputField(desc="实体名称，例如: 魔角效应")
    attributes: str = dspy.InputField(desc="待去重的属性列表（JSON格式）")
    
    deduped_attributes: str = dspy.OutputField(desc="去重后的属性列表（JSON格式）")
    reasoning: str = dspy.OutputField(desc="去重的理由，说明为什么保留这些属性")


# ==================== 步骤2: 创建DSPy模块 ====================

class SmartAttributeDeduplicator(dspy.Module):
    """智能属性去重器"""
    
    def __init__(self):
        super().__init__()
        # 使用ChainOfThought让模型先思考再回答
        self.deduplicate = dspy.ChainOfThought(AttributeDedup)
    
    def forward(self, entity_name: str, attributes: List[str]):
        # 将属性列表转换为字符串
        attributes_str = json.dumps(attributes, ensure_ascii=False, indent=2)
        
        # 调用模型
        result = self.deduplicate(
            entity_name=entity_name,
            attributes=attributes_str
        )
        
        return result


# ==================== 步骤3: 数据转换 ====================

def convert_your_data_to_dspy_format(raw_data_list: List[Dict]) -> List[dspy.Example]:
    """
    将你的知识图谱数据转换为DSPy训练格式
    
    输入格式:
    {
        "head_node": {"properties": {"name": "魔角效应"}},
        "relation": "has_attribute",
        "tail_nodes_to_dedup": [...],
        "deduped_tails": [...]
    }
    
    输出: DSPy训练样本列表
    """
    training_examples = []
    
    for item in raw_data_list:
        # 提取实体名称
        entity_name = item["head_node"]["properties"]["name"]
        
        # 提取待去重属性（输入）
        attributes_to_dedup = item["tail_nodes_to_dedup"]
        
        # 提取去重后属性（标准答案）
        deduped_attributes = item["deduped_tails"]
        
        # 创建DSPy样本
        example = dspy.Example(
            entity_name=entity_name,
            attributes=attributes_to_dedup,
            deduped_attributes=json.dumps(deduped_attributes, ensure_ascii=False),
            reasoning="人工标注的去重结果"  # 可选
        ).with_inputs("entity_name", "attributes")
        
        training_examples.append(example)
    
    return training_examples


# ==================== 步骤4: 评估指标 ====================

def dedup_metric(example, pred, trace=None):
    """
    评估去重效果
    比较预测结果和标准答案的相似度
    """
    try:
        # 解析预测结果
        pred_attrs = json.loads(pred.deduped_attributes)
        # 标准答案
        gold_attrs = json.loads(example.deduped_attributes)
        
        # 转换为集合进行比较
        pred_set = set(pred_attrs)
        gold_set = set(gold_attrs)
        
        # 计算Jaccard相似度
        if len(gold_set) == 0:
            return 1.0 if len(pred_set) == 0 else 0.0
        
        intersection = len(pred_set & gold_set)
        union = len(pred_set | gold_set)
        
        jaccard_score = intersection / union if union > 0 else 0.0
        
        return jaccard_score
        
    except Exception as e:
        print(f"评估出错: {e}")
        return 0.0


# ==================== 步骤5: 训练流程 ====================

def train_with_your_data():
    """使用你的数据训练DSPy模型"""
    
    print("="*80)
    print("🧬 使用知识图谱数据训练DSPy - 属性去重任务")
    print("="*80)
    
    # 1. 准备你的数据（示例）
    your_kg_data = [
        {
            "head_node": {
                "label": "entity",
                "properties": {
                    "name": "魔角效应",
                    "chunk id": "Dwjxk2M8",
                    "schema_type": "MRI伪影"
                }
            },
            "relation": "has_attribute",
            "tail_nodes_to_dedup": [
                "定义:魔角效应伪影，在短TE序列上较为显著，常被误诊为损伤",
                "定义:在关节磁共振扫描过程中，当关节软骨的轴线与主磁场轴形成约55度角时，成像结果表现出更高的信号的现象",
                "定义:在特定角度下MRI信号异常增高的现象",
                "关键角度: 55°",
                "条件: 短TE序列",
                "效果: 局部异常增高的高信号",
                "定义:特殊走向的纤维组织出现虚假的相对高信号",
                "特点:角度依赖性、组织依赖性、TE依赖性",
                "T2弛豫时间延长:最多可延长两倍以上"
            ],
            "dedup_results": {},
            "deduped_tails": [
                "定义:在关节磁共振扫描过程中，当关节软骨的轴线与主磁场轴形成约55度角时，成像结果表现出更高的信号的现象",
                "关键角度: 55°",
                "条件: 短TE序列",
                "效果: 局部异常增高的高信号",
                "特点:角度依赖性、组织依赖性、TE依赖性",
                "T2弛豫时间延长:最多可延长两倍以上"
            ]
        }
    ]
    
    print(f"\n📊 加载数据: {len(your_kg_data)} 个知识图谱样本")
    
    # 2. 转换为DSPy格式
    dspy_examples = convert_your_data_to_dspy_format(your_kg_data)
    print(f"✅ 转换为DSPy格式: {len(dspy_examples)} 个训练样本")
    
    # 3. 划分训练集和测试集
    train_size = int(len(dspy_examples) * 0.8)
    trainset = dspy_examples[:train_size]
    testset = dspy_examples[train_size:]
    
    print(f"📚 训练集: {len(trainset)} 样本")
    print(f"📝 测试集: {len(testset)} 样本")
    
    # 4. 配置DSPy LLM
    print("\n⚙️ 配置DSPy...")
    print("请设置你的LLM配置，例如:")
    print("""
    # OpenAI
    lm = dspy.OpenAI(model="gpt-4o-mini", api_key="your-key")
    
    # Anthropic
    lm = dspy.Claude(model="claude-3-5-sonnet-20241022", api_key="your-key")
    
    # 本地模型（如Ollama）
    lm = dspy.OllamaLocal(model="llama3")
    
    dspy.settings.configure(lm=lm)
    """)
    
    # 取消注释并配置你的LLM
    # lm = dspy.OpenAI(model="gpt-4o-mini")
    # dspy.settings.configure(lm=lm)
    
    # 5. 创建模块
    print("\n🏗️ 创建属性去重模块...")
    deduplicator = SmartAttributeDeduplicator()
    
    # 6. 优化器训练（可选）
    if len(trainset) > 0:
        print("\n🔧 使用BootstrapFewShot优化器训练...")
        print("（需要先配置LLM才能运行）")
        
        # optimizer = BootstrapFewShot(
        #     metric=dedup_metric,
        #     max_bootstrapped_demos=4,
        #     max_labeled_demos=8
        # )
        # 
        # optimized_deduplicator = optimizer.compile(
        #     deduplicator,
        #     trainset=trainset
        # )
        # 
        # print("✅ 训练完成！")
        
        # 7. 评估
        # if len(testset) > 0:
        #     print("\n📊 在测试集上评估...")
        #     from dspy.evaluate import Evaluate
        #     
        #     evaluator = Evaluate(
        #         devset=testset,
        #         metric=dedup_metric,
        #         num_threads=1,
        #         display_progress=True
        #     )
        #     
        #     score = evaluator(optimized_deduplicator)
        #     print(f"测试集得分: {score:.2%}")
    
    # 8. 使用示例
    print("\n"+"="*80)
    print("💡 使用示例")
    print("="*80)
    print("""
    # 使用训练好的模型进行预测
    result = deduplicator(
        entity_name="魔角效应",
        attributes=[
            "定义:魔角效应伪影...",
            "定义:在关节磁共振扫描...",
            "定义:在特定角度下MRI信号..."
        ]
    )
    
    print("去重后的属性:", result.deduped_attributes)
    print("理由:", result.reasoning)
    """)
    
    return deduplicator, dspy_examples


# ==================== 步骤6: 批量数据加载 ====================

def load_kg_data_from_file(filepath: str) -> List[Dict]:
    """
    从JSON文件加载你的知识图谱数据
    
    支持格式:
    1. 单个对象: {...}
    2. 对象数组: [{...}, {...}]
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 如果是单个对象，转换为列表
    if isinstance(data, dict):
        data = [data]
    
    return data


# ==================== 完整训练脚本 ====================

def complete_training_pipeline(data_file: str = None):
    """完整的训练流程"""
    
    print("🚀 DSPy训练流程启动\n")
    
    # 1. 加载数据
    if data_file:
        print(f"📂 从文件加载数据: {data_file}")
        kg_data = load_kg_data_from_file(data_file)
    else:
        print("📂 使用示例数据")
        # 使用内置示例数据
        kg_data = [
            {
                "head_node": {
                    "label": "entity",
                    "properties": {"name": "魔角效应", "chunk id": "xxx", "schema_type": "MRI伪影"}
                },
                "relation": "has_attribute",
                "tail_nodes_to_dedup": [
                    "定义:魔角效应伪影，在短TE序列上较为显著",
                    "定义:在特定角度下MRI信号异常增高的现象",
                    "关键角度: 55°",
                ],
                "deduped_tails": [
                    "定义:在特定角度下MRI信号异常增高的现象",
                    "关键角度: 55°",
                ]
            }
        ]
    
    print(f"✅ 加载了 {len(kg_data)} 个知识图谱样本\n")
    
    # 2. 数据转换
    print("🔄 转换数据格式...")
    dspy_data = convert_your_data_to_dspy_format(kg_data)
    print(f"✅ 转换完成: {len(dspy_data)} 个DSPy样本\n")
    
    # 3. 显示示例
    if len(dspy_data) > 0:
        print("="*80)
        print("📋 样本预览")
        print("="*80)
        example = dspy_data[0]
        print(f"实体: {example.entity_name}")
        print(f"输入属性数量: {len(json.loads(example.attributes))}")
        print(f"去重后属性数量: {len(json.loads(example.deduped_attributes))}")
        print()
    
    # 4. 配置和训练提示
    print("="*80)
    print("⚙️ 配置DSPy并开始训练")
    print("="*80)
    print("""
步骤1: 配置LLM
--------------------------------------
import dspy

# 方式1: OpenAI
lm = dspy.OpenAI(model="gpt-4o-mini", api_key="sk-...")
dspy.settings.configure(lm=lm)

# 方式2: 本地Ollama
lm = dspy.OllamaLocal(model="llama3")
dspy.settings.configure(lm=lm)


步骤2: 训练模型
--------------------------------------
from dspy.teleprompt import BootstrapFewShot

# 创建模块
deduplicator = SmartAttributeDeduplicator()

# 使用优化器
optimizer = BootstrapFewShot(
    metric=dedup_metric,
    max_bootstrapped_demos=4
)

# 训练
optimized_model = optimizer.compile(
    deduplicator,
    trainset=dspy_data[:int(len(dspy_data)*0.8)]
)


步骤3: 保存模型
--------------------------------------
optimized_model.save("./kg_dedup_model.json")


步骤4: 使用模型
--------------------------------------
# 加载
loaded_model = SmartAttributeDeduplicator()
loaded_model.load("./kg_dedup_model.json")

# 预测
result = loaded_model(
    entity_name="魔角效应",
    attributes=["定义1...", "定义2...", "定义3..."]
)
print(result.deduped_attributes)
    """)
    
    return dspy_data


if __name__ == "__main__":
    # 运行训练流程
    # 方式1: 使用示例数据
    dspy_data = complete_training_pipeline()
    
    # 方式2: 从文件加载数据
    # dspy_data = complete_training_pipeline("your_kg_data.json")
    
    print("\n✅ 准备完成！请按照上述步骤配置LLM并开始训练。")
