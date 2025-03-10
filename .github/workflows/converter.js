const fs = require('fs').promises;
const path = require('path');
const MarkdownIt = require('markdown-it');
const highlightjs = require('markdown-it-highlightjs');
const anchor = require('markdown-it-anchor');
const toc = require('markdown-it-toc-done-right');

// Initialize markdown parser with plugins
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})
.use(highlightjs, {
  auto: true,
  inline: true
})
.use(anchor, {
  permalink: anchor.permalink.ariaHidden({
    placement: 'after',
    class: 'anchor',
    symbol: '#',
    ariaHidden: true,
  }),
  level: [1, 2, 3, 4, 5, 6]
})
.use(toc, {
  level: [2, 3],
  listType: 'ul',
  listClass: 'toc-list',
  itemClass: 'toc-item',
  linkClass: 'toc-link'
});

// HTML template with GitHub-like styling
const htmlTemplate = (content, title, tocContent) => `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>
    :root {
      /* GitHub Light Variables */
      --color-canvas-default: #ffffff;
      --color-canvas-subtle: #f6f8fa;
      --color-border-default: #d0d7de;
      --color-border-muted: #d8dee4;
      --color-neutral-muted: rgba(175, 184, 193, 0.2);
      --color-accent-fg: #0969da;
      --color-accent-emphasis: #0969da;
      --color-danger-fg: #cf222e;
      --color-fg-default: #24292f;
      --color-fg-muted: #57606a;
      --color-fg-subtle: #6e7781;
      --color-success-fg: #1a7f37;
      --color-attention-fg: #9a6700;
      --color-header-bg: #24292f;
      --color-header-fg: #ffffff;
      --color-header-logo: #ffffff;
      --color-header-search-bg: #24292f;
      --color-header-search-border: #57606a;
      --color-code-block-bg: #f6f8fa;
      --color-code-block-border: #d0d7de;
    }
    
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
      line-height: 1.5;
      color: var(--color-fg-default);
      background-color: var(--color-canvas-default);
      max-width: 1012px;
      margin: 0 auto;
      padding: 32px;
      font-size: 16px;
    }
    
    /* Layout */
    .markdown-body {
      position: relative;
      margin-bottom: 16px;
      padding: 32px;
      border: 1px solid var(--color-border-default);
      border-radius: 6px;
      background-color: var(--color-canvas-default);
    }
    
    /* Table of Contents */
    .toc-container {
      margin-bottom: 32px;
      padding: 16px;
      background-color: var(--color-canvas-subtle);
      border: 1px solid var(--color-border-default);
      border-radius: 6px;
    }
    
    .toc-header {
      font-size: 16px;
      font-weight: 600;
      margin-top: 0;
      margin-bottom: 8px;
    }
    
    .toc-list {
      padding-left: 20px;
      margin-bottom: 0;
    }
    
    .toc-item {
      margin: 4px 0;
    }
    
    .toc-link {
      color: var(--color-accent-fg);
      text-decoration: none;
    }
    
    .toc-link:hover {
      text-decoration: underline;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
      margin-top: 24px;
      margin-bottom: 16px;
      font-weight: 600;
      line-height: 1.25;
      padding-bottom: 0.3em;
    }
    
    h1 {
      font-size: 2em;
      margin-top: 0;
      border-bottom: 1px solid var(--color-border-muted);
    }
    
    h2 {
      font-size: 1.5em;
      border-bottom: 1px solid var(--color-border-muted);
    }
    
    h3 {
      font-size: 1.25em;
    }
    
    h4 {
      font-size: 1em;
    }
    
    h5 {
      font-size: 0.875em;
    }
    
    h6 {
      font-size: 0.85em;
      color: var(--color-fg-muted);
    }
    
    a {
      color: var(--color-accent-fg);
      text-decoration: none;
    }
    
    a:hover {
      text-decoration: underline;
    }
    
    .anchor {
      float: left;
      padding-right: 4px;
      margin-left: -20px;
      line-height: 1;
      display: inline-block;
      color: var(--color-fg-muted);
      opacity: 0;
      text-decoration: none;
    }
    
    h1:hover .anchor,
    h2:hover .anchor,
    h3:hover .anchor,
    h4:hover .anchor,
    h5:hover .anchor,
    h6:hover .anchor {
      opacity: 1;
    }
    
    /* Text elements */
    p {
      margin-top: 0;
      margin-bottom: 16px;
    }
    
    blockquote {
      padding: 0 1em;
      color: var(--color-fg-muted);
      border-left: 0.25em solid var(--color-border-default);
      margin: 0 0 16px 0;
    }
    
    ul, ol {
      padding-left: 2em;
      margin-top: 0;
      margin-bottom: 16px;
    }
    
    li {
      margin-top: 0.25em;
    }
    
    li + li {
      margin-top: 0.25em;
    }
    
    /* Code */
    code {
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      padding: 0.2em 0.4em;
      margin: 0;
      font-size: 85%;
      background-color: var(--color-neutral-muted);
      border-radius: 6px;
    }
    
    pre {
      font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
      padding: 16px;
      overflow: auto;
      font-size: 85%;
      line-height: 1.45;
      background-color: var(--color-code-block-bg);
      border-radius: 6px;
      margin-top: 0;
      margin-bottom: 16px;
      word-wrap: normal;
      border: 1px solid var(--color-code-block-border);
    }
    
    pre code {
      font-size: 100%;
      padding: 0;
      margin: 0;
      background-color: transparent;
      border: 0;
      white-space: pre;
      word-break: normal;
    }
    
    /* Tables */
    table {
      display: block;
      width: 100%;
      width: max-content;
      max-width: 100%;
      overflow: auto;
      border-spacing: 0;
      border-collapse: collapse;
      margin-top: 0;
      margin-bottom: 16px;
    }
    
    table th {
      font-weight: 600;
    }
    
    table th,
    table td {
      padding: 6px 13px;
      border: 1px solid var(--color-border-default);
    }
    
    table tr {
      background-color: var(--color-canvas-default);
      border-top: 1px solid var(--color-border-muted);
    }
    
    table tr:nth-child(2n) {
      background-color: var(--color-canvas-subtle);
    }
    
    /* Images */
    img {
      max-width: 100%;
      box-sizing: content-box;
      background-color: var(--color-canvas-default);
      border-radius: 6px;
    }
    
    /* Markdown extras */
    hr {
      height: 0.25em;
      padding: 0;
      margin: 24px 0;
      background-color: var(--color-border-default);
      border: 0;
    }
    
    /* GitHub syntax highlighting */
    .hljs-doctag,
    .hljs-keyword,
    .hljs-meta .hljs-keyword,
    .hljs-template-tag,
    .hljs-template-variable,
    .hljs-type,
    .hljs-variable.language_ {
      color: #d73a49;
    }
    
    .hljs-title,
    .hljs-title.class_,
    .hljs-title.class_.inherited__,
    .hljs-title.function_ {
      color: #6f42c1;
    }
    
    .hljs-attr,
    .hljs-attribute,
    .hljs-literal,
    .hljs-meta,
    .hljs-number,
    .hljs-operator,
    .hljs-selector-attr,
    .hljs-selector-class,
    .hljs-selector-id,
    .hljs-variable {
      color: #005cc5;
    }
    
    .hljs-meta .hljs-string,
    .hljs-regexp,
    .hljs-string {
      color: #032f62;
    }
    
    .hljs-built_in,
    .hljs-symbol {
      color: #e36209;
    }
    
    .hljs-comment,
    .hljs-code,
    .hljs-formula {
      color: #6a737d;
    }
    
    .hljs-name,
    .hljs-quote,
    .hljs-selector-tag,
    .hljs-selector-pseudo {
      color: #22863a;
    }
    
    .hljs-deletion {
      color: #b31d28;
      background-color: #ffeef0;
    }
    
    .hljs-addition {
      color: #22863a;
      background-color: #f0fff4;
    }
  </style>
</head>
<body>
  ${tocContent ? `
  <div class="toc-container">
    <h3 class="toc-header">Table of Contents</h3>
    ${tocContent}
  </div>
  ` : ''}
  
  <div class="markdown-body">
    ${content}
  </div>
</body>
</html>
`;

// Export the function for use in Python
module.exports = { 
  convert: async function(mdContent, title) {
    // Generate TOC
    let tocContent = '';
    const contentWithTocPlaceholder = mdContent.includes('[TOC]') 
      ? mdContent 
      : '[TOC]\n\n' + mdContent;
    
    // Convert markdown to HTML
    const htmlContent = md.render(contentWithTocPlaceholder);
    
    // Extract TOC
    const tocMatch = htmlContent.match(/<nav class="table-of-contents">([\s\S]*?)<\/nav>/);
    if (tocMatch) {
      tocContent = tocMatch[1];
    }
    
    // Remove the TOC placeholder from the content
    let contentWithoutToc = htmlContent.replace(/<nav class="table-of-contents">[\s\S]*?<\/nav>/, '');
    
    // Return the final HTML
    return htmlTemplate(contentWithoutToc, title, tocContent);
  }
};
