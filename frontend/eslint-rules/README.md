# ESLint 自定义规则

## 规则列表

### no-emoji

禁止在 UI 文本中使用 emoji 字符，确保前端界面保持专业和简洁。

#### 规则说明

这个规则会检查以下内容：
- 字符串字面量 (`"文本"`)
- 模板字符串 (`` `文本` ``)
- JSX 文本节点
- 对象属性中的字符串值

#### 安装和使用

1. 在 `.eslintrc.js` 或 `.eslintrc.json` 中配置：

```json
{
  "rules": {
    "no-emoji": "error"
  }
}
```

2. 如果使用自定义规则目录：

```json
{
  "rules": {
    "./eslint-rules/no-emoji": "error"
  }
}
```

#### 错误示例

```tsx
// ❌ 错误：包含 emoji
const message = "保存成功 ✅";
const button = <button>点击 👆</button>;
const text = `状态：完成 🎉`;

// ✅ 正确：使用纯文本
const message = "保存成功";
const button = <button>点击</button>;
const text = `状态：完成`;
```

#### 配置选项

无需额外配置，规则开箱即用。

#### 支持的语言

- TypeScript (.ts, .tsx)
- JavaScript (.js, .jsx)
- Vue (.vue)
- JSX/TSX 组件

#### 注意事项

仅检查 UI 文本，不影响：
- 注释中的 emoji
- 文档字符串中的 emoji
- 非用户可见的日志信息
