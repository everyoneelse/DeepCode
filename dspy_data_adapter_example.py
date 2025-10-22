#!/usr/bin/env python3
"""
DSPy 数据适配器示例 - 将知识图谱数据转换为DSPy训练格式
适用于属性去重、实体关系抽取等任务
"""

import json
import dspy
from typing import List, Dict, Any


class KGDataAdapter:
    """知识图谱数据适配器，转换为DSPy训练格式"""
    
    @staticmethod
    def convert_to_dedup_training_data(kg_data_list: List[Dict]) -> List[dspy.Example]:
        """
        转换为属性去重训练数据
        
        Args:
            kg_data_list: 原始知识图谱数据列表
            
        Returns:
            DSPy训练样本列表
        """
        training_examples = []
        
        for item in kg_data_list:
            head_node = item.get("head_node", {})
            entity_name = head_node.get("properties", {}).get("name", "")
            relation = item.get("relation", "")
            
            # 待去重的尾节点
            tail_nodes_to_dedup = item.get("tail_nodes_to_dedup", [])
            # 去重后的尾节点（作为标签）
            deduped_tails = item.get("deduped_tails", [])
            
            if not entity_name or not tail_nodes_to_dedup:
                continue
                
            # 创建DSPy训练样本
            example = dspy.Example(
                entity_name=entity_name,
                relation=relation,
                attributes_to_dedup=tail_nodes_to_dedup,
                deduped_attributes=deduped_tails,
                # 元数据
                schema_type=head_node.get("properties", {}).get("schema_type", ""),
                chunk_id=head_node.get("properties", {}).get("chunk id", "")
            ).with_inputs("entity_name", "relation", "attributes_to_dedup")
            
            training_examples.append(example)
        
        return training_examples
    
    @staticmethod
    def convert_to_kg_extraction_data(kg_data_list: List[Dict]) -> List[dspy.Example]:
        """
        转换为知识图谱提取训练数据
        适用于从文本中提取实体-关系-属性
        """
        training_examples = []
        
        for item in kg_data_list:
            head_node = item.get("head_node", {})
            entity_name = head_node.get("properties", {}).get("name", "")
            relation = item.get("relation", "")
            deduped_tails = item.get("deduped_tails", [])
            
            # 构造上下文文本（模拟原始输入）
            context_text = f"实体: {entity_name}\n关系: {relation}\n属性: {', '.join(deduped_tails)}"
            
            example = dspy.Example(
                context=context_text,
                entity=entity_name,
                relation=relation,
                attributes=deduped_tails
            ).with_inputs("context")
            
            training_examples.append(example)
        
        return training_examples
    
    @staticmethod
    def create_qa_pairs(kg_data_list: List[Dict]) -> List[dspy.Example]:
        """
        从知识图谱数据生成问答对
        用于训练知识问答模型
        """
        qa_examples = []
        
        for item in kg_data_list:
            head_node = item.get("head_node", {})
            entity_name = head_node.get("properties", {}).get("name", "")
            deduped_tails = item.get("deduped_tails", [])
            
            # 生成多个问答对
            questions_templates = [
                f"什么是{entity_name}？",
                f"{entity_name}有什么特点？",
                f"请介绍{entity_name}的定义",
                f"{entity_name}的关键特征是什么？"
            ]
            
            for question in questions_templates:
                # 将属性列表转换为答案
                answer = "\n".join([
                    attr.split("(chunk id:")[0].strip() 
                    for attr in deduped_tails
                ])
                
                example = dspy.Example(
                    question=question,
                    kg_context=json.dumps(item, ensure_ascii=False),
                    answer=answer
                ).with_inputs("question", "kg_context")
                
                qa_examples.append(example)
        
        return qa_examples


# ==================== DSPy 模块定义 ====================

class AttributeDedupSignature(dspy.Signature):
    """属性去重签名"""
    entity_name = dspy.InputField(desc="实体名称")
    relation = dspy.InputField(desc="关系类型")
    attributes_to_dedup = dspy.InputField(desc="待去重的属性列表（可能包含重复或冗余信息）")
    
    deduped_attributes = dspy.OutputField(desc="去重后的属性列表（保留最完整、最准确的描述）")
    reasoning = dspy.OutputField(desc="去重的理由和逻辑")


class KGExtractionSignature(dspy.Signature):
    """知识图谱提取签名"""
    context = dspy.InputField(desc="输入文本或上下文")
    
    entity = dspy.OutputField(desc="提取的实体名称")
    relation = dspy.OutputField(desc="关系类型")
    attributes = dspy.OutputField(desc="属性列表")


class KGQASignature(dspy.Signature):
    """知识图谱问答签名"""
    question = dspy.InputField(desc="用户问题")
    kg_context = dspy.InputField(desc="相关的知识图谱上下文")
    
    answer = dspy.OutputField(desc="基于知识图谱的答案")


# ==================== DSPy 程序模块 ====================

class AttributeDeduplicator(dspy.Module):
    """属性去重模块"""
    
    def __init__(self):
        super().__init__()
        self.dedup = dspy.ChainOfThought(AttributeDedupSignature)
    
    def forward(self, entity_name, relation, attributes_to_dedup):
        result = self.dedup(
            entity_name=entity_name,
            relation=relation,
            attributes_to_dedup=attributes_to_dedup
        )
        return result


class KGExtractor(dspy.Module):
    """知识图谱提取模块"""
    
    def __init__(self):
        super().__init__()
        self.extract = dspy.ChainOfThought(KGExtractionSignature)
    
    def forward(self, context):
        result = self.extract(context=context)
        return result


class KGQA(dspy.Module):
    """知识图谱问答模块"""
    
    def __init__(self):
        super().__init__()
        self.qa = dspy.ChainOfThought(KGQASignature)
    
    def forward(self, question, kg_context):
        result = self.qa(question=question, kg_context=kg_context)
        return result


# ==================== 使用示例 ====================

def example_usage():
    """完整的使用示例"""
    
    # 1. 准备原始数据
    raw_kg_data = [
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
                "定义:魔角效应伪影，在短TE序列上较为显著，常被误诊为损伤 (chunk id: Dwjxk2M8) [attribute]",
                "定义:在关节磁共振扫描过程中，当关节软骨的轴线与主磁场轴形成约55度角时，成像结果表现出更高的信号的现象 (chunk id: LxRPnW2L) [attribute]",
                "定义:在特定角度下MRI信号异常增高的现象 (chunk id: PHuCr1nf) [attribute]",
                "关键角度: 55° (chunk id: PHuCr1nf) [attribute]",
            ],
            "dedup_results": {},
            "deduped_tails": [
                "定义:在关节磁共振扫描过程中，当关节软骨的轴线与主磁场轴形成约55度角时，成像结果表现出更高的信号的现象 (chunk id: LxRPnW2L) [attribute]",
                "关键角度: 55° (chunk id: PHuCr1nf) [attribute]",
            ]
        }
    ]
    
    # 2. 转换为DSPy训练数据
    adapter = KGDataAdapter()
    
    # 转换为去重任务数据
    dedup_train_data = adapter.convert_to_dedup_training_data(raw_kg_data)
    print(f"✅ 转换了 {len(dedup_train_data)} 个属性去重训练样本")
    
    # 转换为知识图谱提取数据
    kg_extraction_data = adapter.convert_to_kg_extraction_data(raw_kg_data)
    print(f"✅ 转换了 {len(kg_extraction_data)} 个知识图谱提取训练样本")
    
    # 转换为问答数据
    qa_data = adapter.create_qa_pairs(raw_kg_data)
    print(f"✅ 转换了 {len(qa_data)} 个问答训练样本")
    
    # 3. 配置DSPy（需要配置LLM）
    # lm = dspy.OpenAI(model="gpt-4o-mini")  # 或其他模型
    # dspy.settings.configure(lm=lm)
    
    # 4. 创建并使用模块
    print("\n" + "="*60)
    print("📊 DSPy模块示例")
    print("="*60)
    
    # 属性去重示例
    deduplicator = AttributeDeduplicator()
    print("\n1️⃣ 属性去重模块已创建")
    # result = deduplicator(
    #     entity_name="魔角效应",
    #     relation="has_attribute",
    #     attributes_to_dedup=raw_kg_data[0]["tail_nodes_to_dedup"]
    # )
    
    # 知识图谱提取示例
    kg_extractor = KGExtractor()
    print("2️⃣ 知识图谱提取模块已创建")
    
    # 问答模块示例
    qa_module = KGQA()
    print("3️⃣ 知识图谱问答模块已创建")
    
    # 5. 优化器配置（可选）
    print("\n" + "="*60)
    print("🔧 DSPy优化器配置建议")
    print("="*60)
    print("""
    # 使用BootstrapFewShot优化
    from dspy.teleprompt import BootstrapFewShot
    
    optimizer = BootstrapFewShot(
        metric=your_metric_function,  # 自定义评估指标
        max_bootstrapped_demos=4,      # 最多使用4个示例
        max_labeled_demos=8            # 最多8个标注样本
    )
    
    # 编译优化后的程序
    optimized_deduplicator = optimizer.compile(
        deduplicator, 
        trainset=dedup_train_data
    )
    """)
    
    return dedup_train_data, kg_extraction_data, qa_data


# ==================== 评估指标 ====================

def dedup_accuracy_metric(example, pred, trace=None):
    """
    属性去重准确率评估
    比较预测的去重结果和标准答案的相似度
    """
    # 简单的集合比较
    pred_set = set(pred.deduped_attributes) if hasattr(pred, 'deduped_attributes') else set()
    gold_set = set(example.deduped_attributes)
    
    if len(gold_set) == 0:
        return 0.0
    
    # 计算Jaccard相似度
    intersection = len(pred_set & gold_set)
    union = len(pred_set | gold_set)
    
    return intersection / union if union > 0 else 0.0


def kg_extraction_f1_metric(example, pred, trace=None):
    """
    知识图谱提取F1评估
    """
    # 实体匹配
    entity_match = 1.0 if pred.entity == example.entity else 0.0
    
    # 关系匹配
    relation_match = 1.0 if pred.relation == example.relation else 0.0
    
    # 属性匹配（简化版）
    pred_attrs = set(pred.attributes) if isinstance(pred.attributes, list) else {pred.attributes}
    gold_attrs = set(example.attributes)
    
    attr_precision = len(pred_attrs & gold_attrs) / len(pred_attrs) if pred_attrs else 0.0
    attr_recall = len(pred_attrs & gold_attrs) / len(gold_attrs) if gold_attrs else 0.0
    attr_f1 = 2 * attr_precision * attr_recall / (attr_precision + attr_recall) if (attr_precision + attr_recall) > 0 else 0.0
    
    # 综合得分
    return (entity_match + relation_match + attr_f1) / 3.0


if __name__ == "__main__":
    print("🧬 DSPy 知识图谱数据适配器")
    print("="*60)
    
    # 运行示例
    dedup_data, extraction_data, qa_data = example_usage()
    
    print("\n✅ 数据转换完成！")
    print(f"   - 属性去重样本: {len(dedup_data)}")
    print(f"   - 知识图谱提取样本: {len(extraction_data)}")
    print(f"   - 问答样本: {len(qa_data)}")
    
    print("\n📝 下一步:")
    print("   1. 配置DSPy LLM (dspy.settings.configure)")
    print("   2. 准备更多训练数据")
    print("   3. 使用优化器训练模块")
    print("   4. 评估和调优")
