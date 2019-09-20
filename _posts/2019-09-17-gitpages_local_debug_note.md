---
layout: post
title: Github Pages 本地调试环境搭建笔记
tags: Github Pages,jekyll,gem,ruby,bundler

---

本文主要记录了 Github Pages 搭建本地调试环境时遇到的问题以及解决方案

## 之前遗留的坑

最近想把许久不更新的博客捡起来，之前就一直卡在 `gem install` 报的 `Gem::FilePermissionError` 错误上，导致无法使用 `Bundler` 让文章在本地预览，只能将写好的文字 push 到线上再修改...这样做的效率实在是很低，于是今天我花了一点时间来研究这个问题。

经过查阅网上的资料，发现原来是因为 MacOS 会预装一版 Ruby，而这版 Ruby 是安装在系统文件夹中的，因此使用这版本的 Ruby ，会将安装的文件

那么有人会想，如果使用 `sudo` 命令能否成功？

我个人认为这样做可能存在一定的风险，因为使用 `sudo` 来执行 `gem install` 时，会将文件写入 `/usr/bin` 中，可能会造成一些无法撤销的问题。因此这里我打算采用另一种方式。

## 在系统中安装其他版本的 Ruby

一个好消息是，我们可以在同一台 Mac 中安装多个版本的 Ruby，在使用 gem install 时采用我们自己下载的 Ruby 即可。话不多说我们马上就开始下载，然后把它安装在 `/user/local` 路径下。

现在市面上有多种工具可以安装，例如 [chruby](#https://github.com/postmodern/chruby) 、 [ruby-install](#https://github.com/postmodern/ruby-install) 、 [rbenv](#https://github.com/rbenv/rbenv) 以及 [RVM](#https://rvm.io/rvm/install) 等等。

我分别使用了 `ruby-install` 和 `rbenv` 两个工具安装了目前最新的 `Ruby`，这两款工具安装很简单，可以很方便的在他们的 `Github` 主页中查到，再将稳定版本的 `Ruby` 安装到电脑中就可以了。

新版本的 `Ruby` 安装好了之后，我们可以用 `which ruby` 来查看当前我们使用的 `Ruby` 已经不在 `/usr/bin` 路径下了，如果使用的是 `ruby-install` 安装，路径会显示为 `/usr/local/ruby` 如果使用的的是 `rbenv` 安装，路径会显示为 `/Users/{用户名}/.rbenv/shims/ruby`，总之现在不是在用系统预装的 `Ruby` ，就能使用 `gem install` 来安装 `Bundler` 了。

## 使用 Bundler 安装 Jekyll

想要在本地预览博客效果，需要使用 `Gemfile` 的内容来构建 `Jekyll` 站点，此时我们需要切换到自己的 `Github Pages` 仓库路径下，查找 `Gemfile` 文件，如果没有，直接新建一个，在里面输入：

```
source 'https://rubygems.org'
gem 'github-pages', group: :jekyll_plugins
```

因为国内访问 ruby 源的速度感人，这里可以把第一行改为 

```
source 'https://gems.ruby-china.com'
```

也可以用 Bundler 的 Gem 源代码镜像命令

```
$ bundle config mirror.https://rubygems.org https://gems.ruby-china.com
```

这样就不用改你的 Gemfile 里的 source了

`Bundler` 安装完成后，切换到自己的 `Github Pages` 仓库路径下，通过 `Bundler` 来安装 `Jekyll` 和其他的依赖项：

```
$ bundle install
```

完成后，即可使用一下命令来启动本地站点服务：

```
$ bundle exec jekyll serve
```

服务启动后，我们可以在浏览器中输入：`http://localhost:4000` 来访问当前路径下对应的站点信息

## 参考链接

https://gems.ruby-china.com

https://help.github.com/en/articles/setting-up-your-github-pages-site-locally-with-jekyll

https://stackoverflow.com/questions/51664716/you-dont-have-write-permissions-for-the-library-ruby-gems-2-3-0-directory

https://www.engineyard.com/blog/how-to-install-ruby-on-a-mac-with-chruby-rbenv-or-rvm