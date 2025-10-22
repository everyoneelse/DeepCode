# 使用你的知识图谱数据训练DSPy - 完整指南

## 📋 目录
1. [数据兼容性分析](#数据兼容性)
2. [快速开始](#快速开始)
3. [详细教程](#详细教程)
4. [常见任务](#常见任务)
5. [最佳实践](#最佳实践)

---

## ✅ 数据兼容性

### 你的数据格式
```json
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
        "定义:魔角效应伪影，在短TE序列上较为显著...",
        "定义:在关节磁共振扫描过程中...",
        ...
    ],
    "dedup_results": {},
    "deduped_tails": [...]
}
```

### ✅ 可以用于DSPy的任务

| 任务类型 | 适用性 | 推荐度 | 说明 |
|---------|--------|--------|------|
| **属性去重** | ✅ 完美匹配 | ⭐⭐⭐⭐⭐ | 你的数据天然包含去重前后对比，非常适合 |
| **知识图谱抽取** | ✅ 适用 | ⭐⭐⭐⭐ | 可以训练实体-关系-属性提取 |
| **知识问答** | ✅ 适用 | ⭐⭐⭐ | 可以基于KG生成问答对 |
| **属性分类** | ✅ 适用 | ⭐⭐⭐⭐ | 将属性分类（定义、特点、条件等） |
| **语义去重** | ✅ 完美匹配 | ⭐⭐⭐⭐⭐ | 识别语义相似的属性描述 |

---

## 🚀 快速开始

### 步骤1: 安装依赖
```bash
pip install dspy-ai
```

### 步骤2: 准备数据文件
将你的知识图谱数据保存为JSON文件 `kg_data.json`:
```json
[
    {
        "head_node": {...},
        "relation": "has_attribute",
        "tail_nodes_to_dedup": [...],
        "deduped_tails": [...]
    },
    ...
]
```

### 步骤3: 运行训练脚本
```bash
python train_dspy_with_kg_data.py
```

### 步骤4: 配置LLM并训练
```python
import dspy

# 配置OpenAI
lm = dspy.OpenAI(model="gpt-4o-mini", api_key="your-key")
dspy.settings.configure(lm=lm)

# 或使用本地模型
lm = dspy.OllamaLocal(model="llama3")
dspy.settings.configure(lm=lm)

# 运行训练
from train_dspy_with_kg_data import complete_training_pipeline
dspy_data = complete_training_pipeline("kg_data.json")
```

---

## 📚 详细教程

### 1. 属性去重任务（推荐）

这是最适合你数据的任务！

#### 为什么适合？
- ✅ 你的数据包含 `tail_nodes_to_dedup`（去重前）和 `deduped_tails`（去重后）
- ✅ 天然的输入-输出对，无需额外标注
- ✅ 可以直接用于训练

#### 示例代码
```python
import dspy
from train_dspy_with_kg_data import (
    SmartAttributeDeduplicator,
    convert_your_data_to_dspy_format,
    dedup_metric
)

# 1. 加载数据
your_data = [
    {
        "head_node": {"properties": {"name": "魔角效应"}},
        "relation": "has_attribute",
        "tail_nodes_to_dedup": [
            "定义:魔角效应伪影...",
            "定义:在关节磁共振扫描...",
            "定义:在特定角度下..."
        ],
        "deduped_tails": [
            "定义:在关节磁共振扫描..."  # 最完整的定义
        ]
    }
]

# 2. 转换格式
dspy_data = convert_your_data_to_dspy_format(your_data)

# 3. 配置LLM
lm = dspy.OpenAI(model="gpt-4o-mini")
dspy.settings.configure(lm=lm)

# 4. 创建并训练
deduplicator = SmartAttributeDeduplicator()

from dspy.teleprompt import BootstrapFewShot
optimizer = BootstrapFewShot(metric=dedup_metric, max_bootstrapped_demos=4)
optimized = optimizer.compile(deduplicator, trainset=dspy_data)

# 5. 使用
result = optimized(
    entity_name="魔角效应",
    attributes=["定义1", "定义2", "定义3"]
)
print(result.deduped_attributes)
```

---

### 2. 知识图谱提取任务

#### 适用场景
从原始文本中提取实体、关系和属性。

#### 示例
```python
import dspy

class KGExtraction(dspy.Signature):
    """从文本中提取知识图谱三元组"""
    text = dspy.InputField(desc="输入医学文本")
    entity = dspy.OutputField(desc="实体名称")
    relation = dspy.OutputField(desc="关系类型")
    attributes = dspy.OutputField(desc="属性列表（JSON）")

class KGExtractor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.extract = dspy.ChainOfThought(KGExtraction)
    
    def forward(self, text):
        return self.extract(text=text)

# 训练数据格式
training_data = [
    dspy.Example(
        text="魔角效应是在关节磁共振扫描中，当软骨轴线与主磁场轴形成约55度角时出现的信号增高现象",
        entity="魔角效应",
        relation="has_attribute",
        attributes='["定义:...", "关键角度: 55°"]'
    ).with_inputs("text")
]
```

---

### 3. 知识问答任务

#### 适用场景
基于知识图谱回答问题。

#### 从你的数据生成QA对
```python
def generate_qa_pairs(kg_item):
    """从KG数据生成问答对"""
    entity_name = kg_item["head_node"]["properties"]["name"]
    attributes = kg_item["deduped_tails"]
    
    qa_pairs = []
    
    # 问题模板
    templates = [
        f"什么是{entity_name}？",
        f"{entity_name}有什么特点？",
        f"请介绍{entity_name}的定义",
    ]
    
    # 答案：合并属性
    answer = "\n".join([
        attr.split("(chunk id:")[0].strip() 
        for attr in attributes
    ])
    
    for question in templates:
        qa_pairs.append({
            "question": question,
            "answer": answer,
            "entity": entity_name
        })
    
    return qa_pairs

# 使用
qa_data = []
for item in your_kg_data:
    qa_data.extend(generate_qa_pairs(item))

# 转换为DSPy格式
dspy_qa_data = [
    dspy.Example(
        question=qa["question"],
        answer=qa["answer"]
    ).with_inputs("question")
    for qa in qa_data
]
```

---

## 🎯 常见任务配置

### 任务1: 属性语义去重
**目标**: 识别并合并语义相似的属性

```python
class SemanticDedup(dspy.Signature):
    entity = dspy.InputField()
    attributes = dspy.InputField(desc="可能包含语义重复的属性列表")
    merged_attributes = dspy.OutputField(desc="合并后的属性，相似的描述只保留最准确的")
    merge_groups = dspy.OutputField(desc="说明哪些属性被合并了")
```

### 任务2: 属性分类
**目标**: 将属性分类（定义、特点、条件、效果等）

```python
class AttributeClassification(dspy.Signature):
    entity = dspy.InputField()
    attribute = dspy.InputField()
    category = dspy.OutputField(desc="属性类别: 定义/特点/条件/效果/其他")
    confidence = dspy.OutputField(desc="分类置信度")
```

### 任务3: 知识图谱补全
**目标**: 基于现有属性预测缺失属性

```python
class KGCompletion(dspy.Signature):
    entity = dspy.InputField()
    existing_attributes = dspy.InputField()
    predicted_attributes = dspy.OutputField(desc="可能缺失的属性")
```

---

## 💡 最佳实践

### 1. 数据准备

#### ✅ 好的做法
```python
# 数据量充足
- 至少 50-100 个标注样本用于训练
- 10-20 个样本用于测试

# 数据质量
- 确保 deduped_tails 是高质量的人工标注
- 属性描述清晰、无歧义
- 去重逻辑一致

# 数据多样性
- 包含不同类型的实体
- 包含不同复杂度的去重场景
```

#### ❌ 避免的问题
```python
# 数据不一致
- tail_nodes_to_dedup 为空
- deduped_tails 包含不在原列表中的属性
- 去重逻辑不一致（有时保留简短描述，有时保留详细描述）
```

### 2. 模型训练

```python
# 推荐配置
optimizer = BootstrapFewShot(
    metric=your_metric,
    max_bootstrapped_demos=4,    # 4-8个示例效果最好
    max_labeled_demos=16,         # 根据数据量调整
    max_rounds=3                  # 多轮优化
)
```

### 3. 评估指标

```python
def comprehensive_dedup_metric(example, pred, trace=None):
    """综合评估指标"""
    
    # 1. 精确匹配得分
    exact_match = 1.0 if pred.deduped_attributes == example.deduped_attributes else 0.0
    
    # 2. Jaccard相似度
    pred_set = set(json.loads(pred.deduped_attributes))
    gold_set = set(json.loads(example.deduped_attributes))
    jaccard = len(pred_set & gold_set) / len(pred_set | gold_set)
    
    # 3. 数量接近度
    size_diff = abs(len(pred_set) - len(gold_set))
    size_penalty = max(0, 1 - size_diff * 0.2)
    
    # 综合得分
    return 0.3 * exact_match + 0.5 * jaccard + 0.2 * size_penalty
```

---

## 📊 数据需求

### 最小数据量
| 任务 | 最小样本数 | 推荐样本数 | 说明 |
|------|-----------|-----------|------|
| 属性去重 | 20 | 100+ | 样本越多，泛化能力越强 |
| KG提取 | 50 | 200+ | 需要覆盖多种实体类型 |
| 知识问答 | 30 | 150+ | 需要多样化的问题模板 |

### 数据扩充技巧
```python
# 1. 从一个KG样本生成多个训练样本
def augment_kg_data(kg_item):
    """数据增强"""
    augmented = []
    
    # 原始样本
    augmented.append(kg_item)
    
    # 随机打乱属性顺序
    shuffled = kg_item.copy()
    import random
    random.shuffle(shuffled["tail_nodes_to_dedup"])
    augmented.append(shuffled)
    
    # 只用部分属性（模拟不完整输入）
    partial = kg_item.copy()
    partial["tail_nodes_to_dedup"] = kg_item["tail_nodes_to_dedup"][:5]
    augmented.append(partial)
    
    return augmented
```

---

## 🔧 故障排查

### 问题1: 训练效果不好
```python
# 可能原因和解决方案
1. 数据量不足 → 增加训练样本或使用数据增强
2. 标注不一致 → 检查并统一去重标准
3. 模型配置不当 → 调整 max_bootstrapped_demos
4. 评估指标不合理 → 使用更宽松的相似度指标
```

### 问题2: 模型过拟合
```python
# 解决方案
1. 增加训练数据多样性
2. 减少 max_bootstrapped_demos
3. 使用正则化技术
4. 添加验证集早停
```

### 问题3: 推理速度慢
```python
# 优化方案
1. 使用更快的模型（如 gpt-4o-mini）
2. 批处理多个样本
3. 缓存常见查询结果
4. 使用本地模型（Ollama）
```

---

## 📖 参考资源

- [DSPy官方文档](https://dspy-docs.vercel.app/)
- [DSPy GitHub](https://github.com/stanfordnlp/dspy)
- [示例代码](./dspy_data_adapter_example.py)
- [训练脚本](./train_dspy_with_kg_data.py)

---

## 🎓 下一步

1. ✅ 检查数据格式是否匹配
2. ✅ 运行示例代码验证流程
3. ✅ 准备足够的训练数据（100+样本）
4. ✅ 配置LLM（OpenAI/Claude/Ollama）
5. ✅ 训练并评估模型
6. ✅ 部署到生产环境

---

## ❓ 常见问题

**Q: 我的数据只有50个样本，够用吗？**  
A: 可以用，但建议至少100个样本以获得更好的泛化能力。可以通过数据增强扩充。

**Q: 必须使用OpenAI API吗？**  
A: 不是，可以使用本地模型（Ollama）、Claude或其他兼容的LLM。

**Q: 训练需要多长时间？**  
A: 使用BootstrapFewShot，100个样本通常需要5-15分钟（取决于LLM速度）。

**Q: 如何评估模型效果？**  
A: 使用测试集评估Jaccard相似度、精确匹配率等指标。

**Q: 可以同时训练多个任务吗？**  
A: 可以，DSPy支持多任务学习，但建议先单独训练每个任务。

---

**祝训练顺利！如有问题，请查看示例代码或提issue。** 🚀
