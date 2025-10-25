# Cursor Agentic Coding 最佳实践

这个指南总结了在使用Cursor编辑器进行agentic coding时的最佳实践，帮助您获得最佳的开发体验和代码质量。

## 核心原则

### 1. 渐进式开发 🔄
- **小步迭代**：每次只实现一个功能模块
- **快速验证**：实现后立即测试功能
- **持续改进**：基于反馈不断优化代码

### 2. 清晰沟通 💬
- **精确描述**：使用具体、明确的语言描述需求
- **提供上下文**：给出足够的背景信息
- **明确期望**：说明预期的输出格式和质量标准

### 3. 结构化思维 🏗️
- **分层设计**：将复杂问题分解为简单的子问题
- **模块化实现**：保持代码的可维护性和可扩展性
- **接口优先**：先定义接口，再实现细节

## Prompt 使用最佳实践

### 1. Prompt 准备

#### 完整性检查
```markdown
在使用prompt前，确保包含：
- [ ] 完整的prompt内容
- [ ] 清晰的输入要求
- [ ] 明确的输出格式
- [ ] 具体的质量标准
```

#### 上下文提供
```markdown
为AI提供充分的上下文：
- 项目背景和目标
- 技术栈和约束条件
- 现有代码结构（如适用）
- 特殊要求和偏好
```

### 2. 输入优化

#### 结构化输入
```markdown
## 项目信息
- 名称：[项目名称]
- 类型：[项目类型]
- 目标：[主要目标]

## 技术要求
- 语言：[编程语言]
- 框架：[使用的框架]
- 数据库：[数据库选择]

## 具体需求
1. [需求1的详细描述]
2. [需求2的详细描述]
3. [需求3的详细描述]

## 约束条件
- [约束1]
- [约束2]
- [约束3]
```

#### 示例驱动
```markdown
提供具体示例：
- 输入示例
- 预期输出示例
- 边界情况示例
- 错误处理示例
```

### 3. 迭代改进

#### 反馈循环
```
1. 提供需求 → 2. 获得输出 → 3. 评估结果 → 4. 提供反馈 → 1. 调整需求
```

#### 增量完善
```markdown
第一轮：实现基本功能
第二轮：添加错误处理
第三轮：优化性能
第四轮：完善文档
```

## 代码质量最佳实践

### 1. 代码结构

#### 标准项目结构
```
project/
├── src/                    # 源代码
│   ├── __init__.py
│   ├── main.py            # 主入口
│   ├── models/            # 数据模型
│   ├── services/          # 业务逻辑
│   ├── utils/             # 工具函数
│   └── config/            # 配置管理
├── tests/                 # 测试代码
│   ├── __init__.py
│   ├── unit/              # 单元测试
│   ├── integration/       # 集成测试
│   └── fixtures/          # 测试数据
├── docs/                  # 文档
├── scripts/               # 脚本文件
├── requirements.txt       # 依赖列表
├── README.md             # 项目说明
└── .gitignore            # Git忽略文件
```

#### 模块化设计
```python
# 好的模块化设计
from src.models.user import User
from src.services.auth import AuthService
from src.utils.validators import validate_email

class UserController:
    def __init__(self):
        self.auth_service = AuthService()
    
    def register(self, email: str, password: str) -> User:
        if not validate_email(email):
            raise ValueError("Invalid email format")
        
        return self.auth_service.create_user(email, password)
```

### 2. 代码规范

#### 命名约定
```python
# 变量和函数：snake_case
user_name = "john_doe"
def get_user_profile():
    pass

# 类：PascalCase
class UserManager:
    pass

# 常量：UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
API_BASE_URL = "https://api.example.com"

# 私有成员：前缀下划线
class User:
    def __init__(self):
        self._private_field = None
        self.__very_private = None
```

#### 文档字符串
```python
def calculate_similarity(text1: str, text2: str, method: str = "cosine") -> float:
    """
    计算两个文本之间的相似度
    
    Args:
        text1 (str): 第一个文本
        text2 (str): 第二个文本
        method (str): 相似度计算方法，可选 'cosine', 'jaccard', 'levenshtein'
    
    Returns:
        float: 相似度分数，范围 [0, 1]
    
    Raises:
        ValueError: 当method参数无效时
        
    Example:
        >>> similarity = calculate_similarity("hello world", "hello python")
        >>> print(f"Similarity: {similarity:.2f}")
        Similarity: 0.45
    """
    if method not in ["cosine", "jaccard", "levenshtein"]:
        raise ValueError(f"Unsupported method: {method}")
    
    # 实现逻辑...
    return 0.0
```

### 3. 错误处理

#### 异常层次
```python
# 自定义异常基类
class AppError(Exception):
    """应用程序基础异常"""
    pass

class ValidationError(AppError):
    """数据验证异常"""
    pass

class AuthenticationError(AppError):
    """认证异常"""
    pass

class DatabaseError(AppError):
    """数据库操作异常"""
    pass
```

#### 错误处理模式
```python
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def safe_api_call(url: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    安全的API调用，包含完整的错误处理
    """
    try:
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        logger.error(f"API call timeout: {url}")
        raise APIError("Request timeout")
        
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error: {url}")
        raise APIError("Connection failed")
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code}: {url}")
        raise APIError(f"HTTP {e.response.status_code}")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise APIError("Unexpected error occurred")
```

### 4. 测试策略

#### 测试金字塔
```
    /\
   /  \    E2E Tests (少量)
  /____\
 /      \   Integration Tests (适量)
/__________\  Unit Tests (大量)
```

#### 单元测试示例
```python
import unittest
from unittest.mock import Mock, patch
from src.services.user_service import UserService
from src.models.user import User

class TestUserService(unittest.TestCase):
    
    def setUp(self):
        """测试前准备"""
        self.user_service = UserService()
        self.mock_user = User(
            id=1,
            email="test@example.com",
            name="Test User"
        )
    
    def test_create_user_success(self):
        """测试用户创建成功场景"""
        # Arrange
        email = "new@example.com"
        name = "New User"
        
        # Act
        result = self.user_service.create_user(email, name)
        
        # Assert
        self.assertIsInstance(result, User)
        self.assertEqual(result.email, email)
        self.assertEqual(result.name, name)
    
    def test_create_user_duplicate_email(self):
        """测试重复邮箱的错误处理"""
        # Arrange
        existing_email = "existing@example.com"
        
        with patch.object(self.user_service, 'email_exists', return_value=True):
            # Act & Assert
            with self.assertRaises(ValidationError):
                self.user_service.create_user(existing_email, "Name")
    
    def tearDown(self):
        """测试后清理"""
        pass
```

## 开发工作流最佳实践

### 1. 版本控制

#### Git 工作流
```bash
# 功能开发流程
git checkout -b feature/user-authentication
git add .
git commit -m "feat: implement user authentication system

- Add login/logout functionality
- Implement JWT token management
- Add password hashing with bcrypt
- Include input validation for auth forms"

git push origin feature/user-authentication
# 创建 Pull Request
```

#### 提交信息规范
```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型说明**：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 2. 代码审查

#### 审查清单
```markdown
## 功能性
- [ ] 代码实现了预期功能
- [ ] 边界情况得到正确处理
- [ ] 错误处理完整且合理

## 代码质量
- [ ] 代码结构清晰，易于理解
- [ ] 命名规范，含义明确
- [ ] 注释和文档完整

## 性能和安全
- [ ] 没有明显的性能问题
- [ ] 安全漏洞已被考虑
- [ ] 资源使用合理

## 测试
- [ ] 单元测试覆盖核心逻辑
- [ ] 集成测试验证功能完整性
- [ ] 测试用例包含边界情况
```

### 3. 持续集成

#### CI/CD 流程
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 src/ tests/
        black --check src/ tests/
        isort --check-only src/ tests/
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 性能优化最佳实践

### 1. 代码层面优化

#### 算法优化
```python
# 低效的实现
def find_duplicates_slow(items):
    duplicates = []
    for i, item in enumerate(items):
        for j, other in enumerate(items[i+1:], i+1):
            if item == other and item not in duplicates:
                duplicates.append(item)
    return duplicates

# 高效的实现
def find_duplicates_fast(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)
```

#### 内存优化
```python
# 使用生成器减少内存占用
def process_large_file(filename):
    """处理大文件，使用生成器避免内存溢出"""
    with open(filename, 'r') as file:
        for line in file:
            yield process_line(line.strip())

# 使用上下文管理器确保资源释放
class DatabaseConnection:
    def __enter__(self):
        self.conn = create_connection()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
```

### 2. 数据库优化

#### 查询优化
```python
# 使用索引和批量操作
class UserRepository:
    def get_users_by_emails(self, emails: List[str]) -> List[User]:
        """批量查询用户，避免N+1问题"""
        return self.session.query(User).filter(
            User.email.in_(emails)
        ).all()
    
    def create_users_batch(self, users_data: List[Dict]) -> List[User]:
        """批量创建用户"""
        users = [User(**data) for data in users_data]
        self.session.bulk_save_objects(users)
        self.session.commit()
        return users
```

#### 缓存策略
```python
from functools import lru_cache
import redis

# 内存缓存
@lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    """使用LRU缓存优化重复计算"""
    # 复杂计算逻辑
    return result

# Redis缓存
class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    def get_cached_result(self, key: str, compute_func, *args, **kwargs):
        """通用缓存装饰器"""
        cached = self.redis_client.get(key)
        if cached:
            return json.loads(cached)
        
        result = compute_func(*args, **kwargs)
        self.redis_client.setex(key, 3600, json.dumps(result))  # 1小时过期
        return result
```

## 安全最佳实践

### 1. 输入验证

#### 数据验证
```python
from pydantic import BaseModel, validator, EmailStr
from typing import Optional

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    age: Optional[int] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and (v < 0 or v > 150):
            raise ValueError('Age must be between 0 and 150')
        return v
```

### 2. 认证和授权

#### JWT 实现
```python
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

class AuthService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """密码验证"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user_id: int, expires_delta: timedelta = None) -> str:
        """创建访问令牌"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode = {"sub": str(user_id), "exp": expire}
        return jwt.encode(to_encode, self.secret_key, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[int]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id = int(payload.get("sub"))
            return user_id
        except jwt.PyJWTError:
            return None
```

### 3. 数据保护

#### 敏感数据处理
```python
import os
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self):
        # 从环境变量获取密钥
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            key = Fernet.generate_key()
            # 在生产环境中，应该安全地存储这个密钥
        self.cipher_suite = Fernet(key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """加密敏感数据"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """解密敏感数据"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
```

## 监控和日志最佳实践

### 1. 日志配置

#### 结构化日志
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        return json.dumps(log_entry)

# 配置日志
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    return logger
```

### 2. 性能监控

#### 性能装饰器
```python
import time
import functools
from typing import Callable

def monitor_performance(func: Callable) -> Callable:
    """性能监控装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                f"Function {func.__name__} executed successfully",
                extra={
                    'execution_time': execution_time,
                    'function_name': func.__name__,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                }
            )
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function {func.__name__} failed",
                extra={
                    'execution_time': execution_time,
                    'function_name': func.__name__,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            )
            raise
    
    return wrapper
```

## 文档最佳实践

### 1. README 结构

#### 完整的 README 模板
```markdown
# 项目名称

简短的项目描述，说明项目的主要功能。

## 功能特性

- ✨ 功能1：描述
- 🚀 功能2：描述
- 🔒 功能3：描述

## 快速开始

### 环境要求

- Python 3.8+
- PostgreSQL 12+
- Redis 6+

### 安装

```bash
# 克隆项目
git clone https://github.com/username/project.git
cd project

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 初始化数据库
python manage.py migrate

# 启动服务
python manage.py runserver
```

### 使用示例

```python
from myproject import MyClass

# 基本用法
instance = MyClass()
result = instance.do_something()
print(result)
```

## API 文档

详细的API文档请访问：http://localhost:8000/docs

## 开发指南

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install

# 运行测试
pytest

# 代码格式化
black src/ tests/
isort src/ tests/
```

### 项目结构

```
project/
├── src/              # 源代码
├── tests/            # 测试
├── docs/             # 文档
├── scripts/          # 脚本
└── requirements.txt  # 依赖
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t myproject .

# 运行容器
docker run -p 8000:8000 myproject
```

### 生产环境

详细的部署指南请参考 [部署文档](docs/deployment.md)

## 贡献

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
```

### 2. API 文档

#### OpenAPI 规范
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="My API",
    description="这是一个示例API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "name": "John Doe"
            }
        }

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """
    获取用户信息
    
    - **user_id**: 用户ID
    
    返回用户的详细信息，包括邮箱和姓名。
    """
    # 实现逻辑
    pass
```

## 团队协作最佳实践

### 1. 代码规范统一

#### EditorConfig 配置
```ini
# .editorconfig
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4

[*.{js,ts,json}]
indent_style = space
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

### 2. 知识共享

#### 技术文档
- 架构决策记录 (ADR)
- 代码规范文档
- 最佳实践指南
- 故障排除手册

#### 代码审查指南
```markdown
## 审查重点

### 功能性
- 代码是否实现了预期功能？
- 边界情况是否得到处理？
- 错误处理是否完整？

### 可读性
- 代码逻辑是否清晰？
- 命名是否恰当？
- 注释是否必要且准确？

### 性能
- 是否存在性能瓶颈？
- 算法复杂度是否合理？
- 资源使用是否高效？

### 安全性
- 输入验证是否充分？
- 是否存在安全漏洞？
- 敏感信息是否得到保护？
```

## 总结

遵循这些最佳实践将帮助您：

1. **提高开发效率**：通过标准化的工作流程和工具
2. **保证代码质量**：通过完善的测试和审查机制
3. **增强可维护性**：通过清晰的架构和文档
4. **促进团队协作**：通过统一的规范和流程
5. **确保项目成功**：通过持续的监控和改进

记住，最佳实践不是一成不变的规则，而是根据项目需求和团队情况灵活调整的指导原则。关键是要保持学习和改进的心态，不断优化开发流程和代码质量。