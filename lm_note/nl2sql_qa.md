# NL2SQL / RAG 架构设计笔记

> 本文不是概念科普，而是一份**工程视角、可落地的设计笔记**，回答在真实系统中：
> - 自然语言如何稳定地转成 SQL
> - 向量检索、chunk、图、多跳各自解决什么问题
> - 大模型在其中应该被“限制”在什么位置

---

## 一、为什么 NL2SQL 不能“直接让模型写 SQL”

### 核心结论

> **NL2SQL 的难点不在 SQL 语法，而在“语义约束与一致性”。**

直接让模型从自然语言生成 SQL，会遇到：
- 乱选字段
- 乱 JOIN
- 编造不存在的列 / 枚举值
- 权限、行级过滤不可控

### 正确拆解方式

NL2SQL 必须被拆成三段：

1. **选 Schema（事实选择）** → 向量检索 + 规则
2. **补约束（系统规则）** → 权限 / 行级 / 强条件
3. **拼 SQL（句法组合）** → LLM

> **模型只负责“拼”，不负责“选”和“判”。**

---

## 二、Schema 为什么要拆成 Chunk

### 结论

> **Schema chunk 不是文档，而是“可推理事实单元”。**

模型生成 SQL 的本质行为是：
- 选字段
- 选条件
- 选 JOIN 路径

所以 Schema 的最小可用单位不是“表”，而是：
- 列
- 枚举
- 关系

---

## 三、Schema Chunk 的标准分类

### 1️⃣ 表 Chunk（弱）

用途：
- 缩小搜索范围
- 锁定主题表

```text
【Schema｜Table】
表名：meta_entity
含义：实体（资源）元数据表
```

> 表 chunk **不能直接生成 SQL**，只能作为入口。

---

### 2️⃣ 列 Chunk（核心）

```text
【Schema｜Column】
表名：meta_entity
字段名：name
含义：实体名称
可用于：SELECT, WHERE LIKE
```

原则：
- **1 列 = 1 chunk**
- 明确可用操作

---

### 3️⃣ 枚举 / 状态 Chunk（必须）

```text
【Schema｜Enum】
表名：meta_entity
字段名：publish_status
取值：
- DRAFT
- PUBLISHED
- OFFLINE
```

> 不显式声明，模型一定会乱造值。

---

### 4️⃣ 关系 Chunk（JOIN 来源）

```text
【Schema｜Relation】
meta_entity.application_code → application.code
关系：多对一
```

> 关系 chunk **只用于 JOIN，不可 SELECT**。

---

## 四、Schema Chunk 能不能直接进向量库？

### 结论

> **不能“裸写”进向量库，必须做语义封装。**

### 必须补充的信息

- chunk 类型（column / enum / relation）
- 可用 SQL 操作
- 禁止行为

### 推荐入库结构

```json
{
  "text": "这是一个 SQL 字段定义：实体名称…",
  "metadata": {
    "kind": "column",
    "table": "meta_entity",
    "column": "name",
    "selectable": true,
    "filterable": true
  }
}
```

> **向量负责“像不像”，结构化字段负责“能不能用”。**

---

## 五、用户问题是如何检索到正确 Chunk 的

### 示例问题

> 查询已发布的实体名称和编码

### 检索流程

1. **问题标准化**
   ```
   查询实体表中发布状态为已发布的实体，返回名称和编码
   ```

2. **向量召回**
   - name 列 chunk
   - code 列 chunk
   - publish_status 枚举 chunk

3. **结构化过滤**
   - 只保留 column / enum
   - 去重

4. **重排序**
   - 列 > 枚举 > 表

5. **交给 LLM 拼 SQL**

```sql
SELECT name, code
FROM meta_entity
WHERE publish_status = 'PUBLISHED'
  AND is_deleted = 0;
```

> `is_deleted = 0` 是系统强约束，不交给模型。

---

## 六、向量检索 vs ES 检索

| 对比项     | ES     | 向量检索        |
| ---------- | ------ | --------------- |
| 匹配方式   | 词项   | 语义            |
| 同义词     | 差     | 强              |
| 结构化过滤 | 强     | 需配合 metadata |
| NL2SQL     | 不适合 | 核心能力        |

> **NL2SQL 选字段，本质是语义匹配，不是关键词匹配。**

---

## 七、为什么有了向量检索还需要大模型

### 向量检索只能做到
- 找“相关信息”

### 但不能做到
- 组合字段
- 生成 SQL 结构
- 推断 GROUP BY / 聚合

> **向量检索选材料，LLM 负责做菜。**

---

## 八、什么是多跳？什么不是多跳？

### 真 · 多跳（Multi-hop）

必要条件：
1. 下一步依赖上一步结果
2. 有明确推理顺序

```text
meta_entity → application → user → email
```

---

### 不是多跳的情况

- 一次问题命中多个 chunk
- 一个 SQL 里有多个 JOIN，但路径是确定的

> **JOIN 多 ≠ 多跳推理**

---

## 九、图数据库 vs Chunk + LLM

| 维度         | 图数据库 | Chunk + LLM |
| ------------ | -------- | ----------- |
| 关系是否确定 | 是       | 不一定      |
| 多跳遍历     | 强       | 需约束      |
| 自然语言     | 弱       | 强          |
| Schema 变化  | 敏感     | 容忍        |

### 结论

> **图数据库解决“怎么走”，
> Chunk + LLM 解决“该往哪走”。**

---

## 十、知识库 / RAG 的核心工程原则

### 1️⃣ 知识拆分

- 人：定规则
- 工具：切数据
- 抽样：纠偏

### 2️⃣ Chunk 质量标准

- 单一事实
- 条件完整
- 可独立回答

### 3️⃣ 重复是检索友好

- 关键上下文允许重复
- 但结论不能混合

---

## 十一、一句话总纲（压轴）

> **NL2SQL / RAG 的本质不是“让模型更聪明”，
> 而是“让模型更不自由”。**

当你把：
- Schema 事实
- 推理边界
- 系统约束

都设计清楚之后，模型自然就“看起来很准”。

---

**并非一个表一个列一个chunk，要根据情况合并，比如一个chunk有多个列的描述，或者某些可能相关性较高的放在一个chunk，避免chunk召回效率低。**

