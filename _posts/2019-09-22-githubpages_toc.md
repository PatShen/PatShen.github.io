---
layout: post
title: Github Pages 的 markdown 文档中自动生成索引
tag: markdown, kramdown, toc, github pages, jekyll

---

* TOC
{:toc}

## 背景

所谓的 `自动生成索引` 在 markdown 中指的是 `TOC(Table of Contents)`，我们知道，在 markdown 语法中可以使用 `#` 表示一级标题，`##` 表示二级标题，以此类推... 

通过 `TOC` 可以让我们在文章的开头就把文章中的标题单独显示出来。这个特性可以帮助读者更好的理解文章的结构，从而更好的理解作者的文章内容。

现在市面上很多使用 `markdown` 作为文档的网站都支持 `TOC` ，但是使用 `jekyll` 生成的 `Github Pages` 并不支持这一特性，这让很多像笔者一样的使用 `jekyll` 生成博客的作者很是苦恼。

## 探索

那么有没有什么方法可以让使用 `jekyll` 的 `Github Pages` 也支持 `TOC` 特性吗？

### 原理

经过查阅资料，我们发现 `jekyll` 默认使用 `Kramdown` 来解析 `markdown` 并且将其转换成 `HTML` 页面。

`Kramdown` 在转换时默认会将标题生成一个对应的 ID，同时也会将自动生成的 ID 添加到索引中。

有关 `Kramdown` 自动生成 ID 的规则以及 ID 对应的顶部索引，可以在 [Automatic Generation of Header IDs](https://kramdown.gettalong.org/converter/html.html#auto-ids) 和 [Automatic “Table of Contents” Generation](https://kramdown.gettalong.org/converter/html.html#toc) 查询到。

### 实现

`Kramdown` 索引支持 `有序列表` 和 `无序列表` 两种表现形式，实际使用时，只需要将以下格式添加到自己的文章中，格式如下：

```
1. 有序列表（此处可写任意字符串）
{:toc}
```

```
* 无序列表（此处可写任意字符串）
{:toc}
```

### 特殊情况

`Kramdown` 也支持不将某些标题显示在索引上，此时只需要在 `该标题` 下方加上 `{:.no_toc}` 即可。

### 实例介绍

```
* toc
{:toc}

# 一号标题

## 二号标题

### 三号标题
{:.no_toc}
```

## 参考链接

[How to generate a Table of Contents (ToC) on a rendered Github Pages README.md?](https://stackoverflow.com/questions/54243424/how-to-generate-a-table-of-contents-toc-on-a-rendered-github-pages-readme-md)

[Jekyll Markdown Options](https://jekyllrb.com/docs/configuration/markdown/)

[How I Add a Table of Contents to my Jekyll Blog Written in Markdown](http://www.seanbuscay.com/blog/jekyll-toc-markdown/)

[Kramdown HTML Converter](https://kramdown.gettalong.org/converter/html.html)