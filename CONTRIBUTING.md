# 贡献指南

感谢你对本项目的关注！欢迎所有形式的贡献 🎉

## 🤝 如何贡献

### 报告 Bug

如果你发现了 Bug，请：

1. 先在 Issues 中搜索是否已有相同问题
2. 如果没有，创建新 Issue，尽可能详细地描述：
   - Bug 的复现步骤
   - 预期行为
   - 实际行为
   - 环境信息（操作系统、Python 版本等）
   - 相关的错误日志或截图

### 提出新功能

1. 在 Issues 中创建 Feature Request
2. 清晰描述：
   - 你希望添加什么功能
   - 为什么需要这个功能
   - 可能的实现思路（可选）

### 提交代码

#### 1. Fork 并克隆项目

```bash
# Fork 本仓库后
git clone https://github.com/YOUR_USERNAME/PROJECT_NAME.git
cd PROJECT_NAME
```

#### 2. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

#### 3. 开发环境设置

```bash
# 使用 uv 创建虚拟环境
uv venv
.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate  # Linux/macOS

# 安装依赖
pip install -r requirements.txt
```

#### 4. 开发并测试

- 确保代码符合现有代码风格
- 添加必要的注释和文档
- 测试你的更改

#### 5. 提交更改

```bash
git add .
git commit -m "feat: 简洁描述你的更改"
```

**提交信息规范**：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `style:` 代码格式调整（不影响功能）
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

#### 6. 推送并创建 Pull Request

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request，描述清楚：

- 你做了什么更改
- 为什么要做这个更改
- 如何测试这些更改

## 🔍 PR 审核流程

1. 提交 PR 后，项目维护者会进行审核
2. 可能会有讨论和修改建议
3. 通过审核后会被合并到主分支

## 💡 其他贡献方式

- ⭐ Star 本项目
- 📢 分享给其他开发者
- 📖 改进文档
- 💬 帮助回答 Issues 中的问题

## 📧 联系方式

如有任何问题，可以通过以下方式联系：

- GitHub Issues
- 邮箱：os.dev.hongjun@gmail.com

感谢你的贡献！🙏
