---
layout: post
title: Python3安装笔记（MacOS）
lag: python,macos

---

* TOC
{:toc}

# 安装方式
homebrew

# 命令行
brew install python3 && cp /usr/local/bin/python3 /usr/local/bin/python

# 依赖

gdbm, readline, sqlite, xz

## 一些可能有用的log

## readline

```
readline is keg-only, which means it was not symlinked into /usr/local,
because macOS provides the BSD libedit library, which shadows libreadline.
In order to prevent conflicts when programs look for libreadline we are
defaulting this GNU Readline installation to keg-only.

For compilers to find readline you may need to set:
  export LDFLAGS="-L/usr/local/opt/readline/lib"
  export CPPFLAGS="-I/usr/local/opt/readline/include"
```

## sqlite

```
  sqlite is keg-only, which means it was not symlinked into /usr/local,
because macOS provides an older sqlite3.

If you need to have sqlite first in your PATH run:
  echo 'export PATH="/usr/local/opt/sqlite/bin:$PATH"' >> ~/.bash_profile

For compilers to find sqlite you may need to set:
  export LDFLAGS="-L/usr/local/opt/sqlite/lib"
  export CPPFLAGS="-I/usr/local/opt/sqlite/include"
```
## 其它
  
命令行会先更新 homebrew，如果嫌慢可以先 ctrl+c 跳过