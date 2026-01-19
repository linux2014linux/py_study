## 常见的chunk拆分方法
### 语义单元拆分
一个 chunk = 一个完整知识点, 适合技术文档、说明文和教程类拆分, 保证 chunk 可独立理解。
如**代码基于AST拆分**。
#### 示例
原文
```
员工每年有 10 天年假，需提前 3 天申请，经直属主管审批后方可生效。
病假需提供医院出具的病假证明，可在事后补交，工资按公司规定执行。
所有请假申请需通过公司 OA 系统提交。
```
**原则**：一个 chunk = 一个可独立理解的知识点
* Chunk 1：年假规则
```json
{
  "chunk_id": "chunk_001",
  "text": "员工每年有 10 天年假，需提前 3 天申请，经直属主管审批后方可生效。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "section": "年假",
    "entity": "AnnualLeave",
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```
* Chunk 2：病假规则
```json
{
  "chunk_id": "chunk_002",
  "text": "病假需提供医院出具的病假证明，可在事后补交，工资按公司规定执行。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "section": "病假",
    "entity": "SickLeave",
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```
* Chunk 3：请假审批流程
```json
{
  "chunk_id": "chunk_003",
  "text": "所有请假申请需通过公司 OA 系统提交，审批通过后方可视为有效请假。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "section": "审批流程",
    "entity": "LeaveApplicationProcess",
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```

### 层级结构拆分
按章 / 节 / 小节切分, 如规范、手册和设计文档等, 利用文档结构，chunk 携带上下文。
#### 示例
原文:
```
员工请假制度
公司支持多种请假类型，包括年假、病假和事假。

年假
员工每年有 10 天带薪年假，需提前 3 天提交申请，经直属主管审批后方可生效。

病假
病假需提供医院出具的病假证明，可在事后补交，工资按公司相关规定执行。

审批流程
所有请假申请需通过公司 OA 系统提交，审批通过后方可视为有效请假。
```
**原则**：每个 chunk = 文档的一个章节 / 小节 + 上层上下文
* Chunk 1：年假
```json
{
  "chunk_id": "chunk_001",
  "text": "员工每年有 10 天带薪年假，需提前 3 天提交申请，经直属主管审批后方可生效。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "title": "员工请假制度",
    "section": "年假",
    "section_path": ["员工请假制度", "年假"],
    "entity": "AnnualLeave",
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```
* Chunk 2：病假
```json
{
  "chunk_id": "chunk_002",
  "text": "病假需提供医院出具的病假证明，可在事后补交，工资按公司相关规定执行。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "title": "员工请假制度",
    "section": "病假",
    "section_path": ["员工请假制度", "病假"],
    "entity": "SickLeave",
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```
* Chunk 3：审批流程
```json
{
  "chunk_id": "chunk_003",
  "text": "所有请假申请需通过公司 OA 系统提交，审批通过后方可视为有效请假。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "title": "员工请假制度",
    "section": "审批流程",
    "section_path": ["员工请假制度", "审批流程"],
    "entity": "LeaveApplicationProcess",
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```

### 滑动窗口拆分
相邻 chunk 共享部分内容, 如长文档、上下文连续文本, 用 overlap 防止语义断裂。
#### 示例
原文:
```
员工请假制度

公司支持多种请假类型，包括年假、病假和事假。

年假
员工每年有 10 天带薪年假，需提前 3 天提交申请，经直属主管审批后方可生效。

病假
病假需提供医院出具的病假证明，可在事后补交，工资按公司相关规定执行。

事假
事假需提前 1 天申请，经主管审批后生效，无薪。

审批流程
所有请假申请需通过公司 OA 系统提交，审批通过后方可视为有效请假。
```
**原则**
* chunk size：120 tokens（可按实际模型调整）
* overlap：40 tokens（防止断义）
* chunk 内容可以跨原文段落，保证上下文连续
* Chunk 1
```json
{
  "chunk_id": "chunk_001",
  "text": "员工请假制度\n公司支持多种请假类型，包括年假、病假和事假。\n员工每年有 10 天带薪年假，需提前 3 天提交申请，经直属主管审批后方可生效。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "section_path": ["员工请假制度", "年假"],
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```
* Chunk 2（包含 overlap）
```json
{
  "chunk_id": "chunk_002",
  "text": "员工每年有 10 天带薪年假，需提前 3 天提交申请，经直属主管审批后方可生效。\n病假需提供医院出具的病假证明，可在事后补交，工资按公司相关规定执行。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "section_path": ["员工请假制度", "病假"],
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```
* Chunk 3
```json
{
  "chunk_id": "chunk_003",
  "text": "病假需提供医院出具的病假证明，可在事后补交，工资按公司相关规定执行。\n事假需提前 1 天申请，经主管审批后生效，无薪。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "section_path": ["员工请假制度", "事假"],
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```
* Chunk 4
```json
{
  "chunk_id": "chunk_004",
  "text": "事假需提前 1 天申请，经主管审批后生效，无薪。\n所有请假申请需通过公司 OA 系统提交，审批通过后方可视为有效请假。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "section_path": ["员工请假制度", "审批流程"],
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```

### Q/A 导向拆分
围绕“用户会问的问题”切, 如FAQ、规则说明, 提高问题 → chunk 的命中率。
#### 示例
原文:
```
员工请假制度

公司支持多种请假类型，包括年假、病假和事假。

年假
员工每年有 10 天带薪年假，需提前 3 天提交申请，经直属主管审批后方可生效。

病假
病假需提供医院出具的病假证明，可在事后补交，工资按公司相关规定执行。

事假
事假需提前 1 天申请，经主管审批后生效，无薪。

审批流程
所有请假申请需通过公司 OA 系统提交，审批通过后方可视为有效请假。
```
**原则**
* chunk = 一个“问答对”
* 问题可以是用户真实会问的
* 答案是文档中可独立回答该问题的内容
Chunk 1：请假类型
```json
{
  "chunk_id": "chunk_001",
  "text": "Q：公司支持哪些请假类型？\nA：公司支持多种请假类型，包括年假、病假和事假。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "section": "请假类型",
    "entity": "LeaveTypes",
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```
Chunk 2：年假规则
```json
{
  "chunk_id": "chunk_002",
  "text": "Q：员工年假是多少天？如何申请？\nA：员工每年有 10 天带薪年假，需提前 3 天提交申请，经直属主管审批后方可生效。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "section": "年假",
    "entity": "AnnualLeave",
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```
Chunk 3：病假规则
```json
{
  "chunk_id": "chunk_003",
  "text": "Q：病假如何申请？需要提供什么材料？\nA：病假需提供医院出具的病假证明，可在事后补交，病假期间工资按公司相关规定执行。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "section": "病假",
    "entity": "SickLeave",
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```
Chunk 4：事假规则
```json
{
  "chunk_id": "chunk_004",
  "text": "Q：事假如何申请？是否带薪？\nA：事假需提前 1 天申请，经主管审批后生效，无薪。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "section": "事假",
    "entity": "PersonalLeave",
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```
Chunk 5：审批流程
```json
{
  "chunk_id": "chunk_005",
  "text": "Q：请假申请如何生效？\nA：所有请假申请需通过公司 OA 系统提交，审批通过后方可视为有效请假。",
  "metadata": {
    "doc_id": "leave_policy_2026",
    "section": "审批流程",
    "entity": "LeaveApplicationProcess",
    "source": "HR制度文档",
    "created_at": "2026-01-16"
  }
}
```

### 实体中心拆分
一个 chunk 围绕一个业务实体, 如系统说明、API和数据字典, 为多跳、实体检索做准备。
#### 示例
原文: 也可能直接就是表结构。
```
school (
  id BIGINT PRIMARY KEY COMMENT '学校唯一ID',
  school_name VARCHAR(100) COMMENT '学校名称'
)
class (
  id BIGINT PRIMARY KEY COMMENT '班级唯一ID',
  school_id BIGINT COMMENT '所属学校ID',
  grade INT COMMENT '年级'
)
student (
  id BIGINT PRIMARY KEY COMMENT '学生唯一ID',
  class_id BIGINT COMMENT '所属班级ID',
  name VARCHAR(50) COMMENT '学生姓名',
  enrollment_year INT COMMENT '入学年份'
)
```
Chunk1: school 表
```json
{
  "chunk_id": "entity_table_school",
  "text": "school 表用于存储学校的基础信息，是学校维度的主表。",
  "metadata": {
    "entity_name": "school",
    "entity_type": "mysql_table",
    "primary_key": "id",
    "columns": [
      {
        "name": "id",
        "type": "BIGINT",
        "description": "学校唯一ID",
        "nullable": false,
        "example": 1001
      },
      {
        "name": "school_name",
        "type": "VARCHAR(100)",
        "description": "学校名称",
        "nullable": false,
        "example": "第一中学"
      }
    ],
    "relations": {
      "has_many": {
        "table": "class",
        "join": "school.id = class.school_id"
      }
    },
    "doc_id": "db_schema_doc",
    "source": "数据库设计文档"
  }
}
```
Chunk2: class 表
```json
{
  "chunk_id": "entity_table_class",
  "text": "class 表用于存储班级信息，每个班级隶属于一个学校，是学校与学生之间的中间表。",
  "metadata": {
    "entity_name": "class",
    "entity_type": "mysql_table",
    "primary_key": "id",
    "columns": [
      {
        "name": "id",
        "type": "BIGINT",
        "description": "班级唯一ID",
        "nullable": false,
        "example": 2001
      },
      {
        "name": "school_id",
        "type": "BIGINT",
        "description": "所属学校ID，关联 school.id",
        "nullable": false,
        "example": 1001
      },
      {
        "name": "grade",
        "type": "INT",
        "description": "年级，例如 1 表示一年级",
        "nullable": false,
        "example": 3
      }
    ],
    "foreign_keys": {
      "school_id": "school.id"
    },
    "relations": {
      "belongs_to": "school",
      "has_many": {
        "table": "student",
        "join": "class.id = student.class_id"
      }
    },
    "doc_id": "db_schema_doc",
    "source": "数据库设计文档"
  }
}
```
Chunk3: student表
```json
{
  "chunk_id": "entity_table_student",
  "text": "student 表用于存储学生的基本信息，是学生维度的主表。",
  "metadata": {
    "entity_name": "student",
    "entity_type": "mysql_table",
    "primary_key": "id",
    "columns": [
      {
        "name": "id",
        "type": "BIGINT",
        "description": "学生唯一ID",
        "nullable": false,
        "example": 30001
      },
      {
        "name": "class_id",
        "type": "BIGINT",
        "description": "所属班级ID，关联 class.id",
        "nullable": false,
        "example": 2001
      },
      {
        "name": "name",
        "type": "VARCHAR(50)",
        "description": "学生姓名",
        "nullable": false,
        "example": "张三"
      },
      {
        "name": "enrollment_year",
        "type": "INT",
        "description": "入学年份，例如 2023",
        "nullable": false,
        "example": 2023
      }
    ],
    "foreign_keys": {
      "class_id": "class.id"
    },
    "relations": {
      "belongs_to": "class"
    },
    "doc_id": "db_schema_doc",
    "source": "数据库设计文档"
  }
}
```
### 写向量库示例
```python
chunk_text = (
    "student 表用于存储学生信息。"
    "每个学生隶属于一个班级，包含学号、姓名和入学年份。"
    "student 表通过 class_id 字段与 class 表关联。"
)
# 这里是通用的, 向量化的内容各个 chunk 结构中的 text
embedding = model.get_embedding(chunk_text)
vector_record = {
    "chunk_id": "entity_table_student",
    "embedding": embedding.tolist(),
    "text": chunk_text,
    "metadata": {
        "entity_name": "student",
        "entity_type": "mysql_table",
        "columns": ["id", "class_id", "name", "enrollment_year"],
        "primary_key": "id",
        "foreign_keys": {
            "class_id": "class.id"
        },
        "relations": {
            "belongs_to": "class"
        },
        "doc_id": "db_schema_doc",
        "source": "数据库设计文档"
    }
}
vector_db.upsert(vector_record)
```
### 5中方法对比

### 工程实践中建议
通常是多种方法组合使用。
* 怕答不全 → 滑动窗口
* 怕召回歪 → Q/A 导向
* 要做多跳 → 实体中心
* 要长期维护 → 层级结构
* 想稳不翻车 → 语义单元