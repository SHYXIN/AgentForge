/**
 * ESLint 规则：禁止在 UI 文本中使用 emoji
 *
 * 这个规则检查字符串字面量、JSX 文本和模板字符串中是否包含 emoji 字符，
 * 确保前端界面使用纯文本，保持专业和简洁。
 */

module.exports = {
  meta: {
    type: 'suggestion',
    docs: {
      description: '禁止在 UI 文本中使用 emoji',
      category: 'Stylistic Issues',
      recommended: true,
    },
    fixable: null,
    schema: [],
    messages: {
      noEmoji: '避免在 UI 文本中使用 emoji 字符。请使用纯文本替代。',
    },
  },

  create(context) {
    // 匹配常见 emoji 的正则表达式
    const emojiRegex = /[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]|[\u{1F900}-\u{1F9FF}]|[\u{1FA00}-\u{1FA6F}]|[\u{1FA70}-\u{1FAFF}]/gu;

    /**
     * 检查字符串是否包含 emoji
     * @param {string} value - 要检查的字符串
     * @returns {boolean} 是否包含 emoji
     */
    function hasEmoji(value) {
      if (typeof value !== 'string') return false;
      return emojiRegex.test(value);
    }

    /**
     * 报告包含 emoji 的节点
     * @param {ASTNode} node - AST 节点
     * @param {string} value - 包含 emoji 的字符串值
     */
    function reportEmoji(node, value) {
      context.report({
        node,
        messageId: 'noEmoji',
        data: {
          value,
        },
      });
    }

    return {
      // 检查字符串字面量
      Literal(node) {
        if (hasEmoji(node.value)) {
          reportEmoji(node, node.value);
        }
      },

      // 检查模板字符串
      TemplateElement(node) {
        if (hasEmoji(node.value.raw)) {
          reportEmoji(node, node.value.raw);
        }
      },

      // 检查 JSX 文本
      JSXText(node) {
        if (hasEmoji(node.value)) {
          reportEmoji(node, node.value);
        }
      },
    };
  },
};
