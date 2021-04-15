---
layout: post
title: GitLab-Fastlane-CI
tag: GitLab, fastlane, CI, iOS

---

* TOC
{:toc}

# 概述

Gitlab 自带了一套 CI，通过注册 Runner，关联 gitlab-ci.yml，触发相应的操作。


# 安装Runner

* `curl` 
* `homebrew`

https://docs.gitlab.com/runner/install/osx.html

# 注册 Runner

```
gitlab-runner reigister
```

https://docs.gitlab.com/runner/register/


> 需要注意的是：注册 Runner 填写的 tag，需要和 ci.yml 文件中的 tag 对应


# 配置 gitlab-ci.yml

## 按照条件触发 CI

可以在 workflow 或者具体的流程中添加 rules

```
workflow:
    rules:
        - if: $CI_COMMIT_BRANCH == "master" // 完全匹配
        ...
        - if: $CI_COMMIT_BRANCH =~ /master/ // 正则表达式
        ...
        - when: never // 否则不做处理
```

常用的条件参数：

* `$CI_PIPELINE_SOURCE`: 事件
* `$CI_COMMIT_BRANCH`: 分支
* `$CI_COMMIT_MESSAGE`: 提交信息

具体文档见：https://docs.gitlab.com/ee/ci/yaml/README.html#rules

# xcpretty

## 安装

全局环境变量增加：

```
export PATH="/usr/local/bin:$PATH"
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
```

命令行执行： `sudo gem install -n /usr/local/bin xcpretty`

## 问题

如果用 `sudo gem install xcpretty` 命令安装，直接调用命令会出现 `xcpretty: command not found` 的情况

参考了：https://www.jianshu.com/p/efeef0b70391

# 参考链接

* https://juejin.cn/post/6944878021560139783
* https://columns.chicken-house.net/2017/08/05/what-cicd-do-you-need/
* https://juejin.cn/post/6844904184219697160
* https://www.jianshu.com/p/efeef0b70391
* https://docs.gitlab.com/ee/ci/yaml/README.html#rules
