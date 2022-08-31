---
layout: post
title: 记一个 git pull 超时问题的解决办法
tag: Git

---

* TOC
{:toc}

> 本文的解决方案能够解决使用 `ssh` 拉取代码超时的问题，对于其他类似问题，不一定有效。

# 背景

最近经常遇到从 Github 拉取仓库代码超时的现象，给我的工作、学习带来很大的干扰，于是我决定找找问题的解决方案。

# 分析

其实这个情况之前也遇到过，我之前采用了全局挂梯子的方式，不是很方便。最近因为一些特殊情况，尝试使用了手机热点，发现也可以解决这个问题。

于是我产生了一些疑问，是不是因为某些`配置`导致了这个情况发生？

> 不仅仅是 Github，另一个代码托管工具 Bitbucket 也出现了相似的情况：
> 
> 在 Wi-Fi 下，pull 会超时，使用移动网络不会，而且速度还挺快，能达到 2MB/s 以上。

在一次查找这个问题的解决方案的过程中，我无意发现了[这篇文章](https://jasonkayzk.github.io/2019/10/10/关于使用Git时push-pull超时-以及Github访问慢的解决办法/)。
我遇到的情况和这篇文章的作者类似，同时他还提到可能是 ssh 配置存在问题导致了超时。

> ssh 是专为远程登录会话和其他网络服务提供安全性的协议，它的默认端口是 22。
> 
> 我们在拉取代码时超时，大概率的原因就是这个端口被阻塞了。
> 
> 所以如果我们能够打通22端口，或者使用其他端口运行 ssh，就能够解决这个问题。


# 解决办法

使用其他端口运行 ssh，在当前用户目录下（MacOS）的 ssh 配置文件（~/.ssh/config）中，加入以下内容

```
Host github.com
Hostname ssh.github.com
Port 443
```

对于 Bitbucket，可以加入以下内容：

```
Host bitbucket.org
Hostname altssh.bitbucket.org
Port 443
```
这样我们的 ssh 将会使用 443端口，保存后就可以正常拉取代码了。

> 如果 config 文件不存在，就直接新建一个。

# 扩展阅读

为什么 ssh 的 22 端口会被阻塞？

# 参考链接

* [关于使用Git时push-pull超时-以及Github访问慢的解决办法](https://jasonkayzk.github.io/2019/10/10/关于使用Git时push-pull超时-以及Github访问慢的解决办法/)
* [ssh: connect to host github.com port 22: Connection timed out](https://stackoverflow.com/a/52817036)
* [ssh: connect to host bitbucket.org port 22: Connection timed out](https://stackoverflow.com/a/46492615)
* [https://gist.github.com/goddoe/5692bfc3cdc374d918a87882963edf36](https://gist.github.com/goddoe/5692bfc3cdc374d918a87882963edf36)
