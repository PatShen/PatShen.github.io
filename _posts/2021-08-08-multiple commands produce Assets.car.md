---
layout: post
title: Multiple commands produce Assets.car 的错误解决办法
tag: iOS, cocapods, assets

---

* TOC
{:toc}

# 概述

最近在公司项目中接入腾讯 IM SDK 发现了如题的报错：`Multiple commands produce Assets.car`，搜索了一下，这个错误的原因是：

* 在 `New Build System` 环境下，Copy Resources 构建阶段会把工程里的 xcassets 包合并到一个 `Assets.car` 文件
* 此时如果你集成了其他 pod，而这些 pod 也有对应的 assets，那么编译时它们也会创建 `Assets.car`，会与主工程重名

这就造成了这个错误。

# 解决办法

目前有很多办法可以解决这个问题，我们可以根据实际情况，选择最合适的方式解决。

## 修改编译环境

前面说到，这个问题是在 xcode 10 新增的 `New Build System` 环境下发生的，我们可以将其改为原来的 `Legacy Build System`。

> 这是最快的解决办法，但不一定是长久之计，如果苹果突然有一天把 `Legacy Build System` 取消了，这个办法就失效了。

## 修改 Podfile 的配置

在主工程的 Podfile 中加上这句：

```ruby
install! 'cocoapods', :disable_input_output_paths => true
```

这句代码会禁用 cocoapods 在编译时的复制操作，从而每次编译都重新创建（而非复制）。

> 这种方式的缺点：
> 
> 一是会增加构建过程中的额外开销（创建资源明显比复制资源要慢）
> 
> 二是如果你的工程在构建过程中需要复制自己定义的一些文件时，用这种方式就不太合适了。

## 删除主工程 Build Phase 中的 "Output file lists"

在 XCode 的 `build phase` 中搜索 `[CP] Copy Pods Resources`，将 `Output file lists` 中的路径手动删掉。

> 这也能解决这个问题，但是你每次 pod install 之后都得手动操作一次...（好蠢）。不推荐

我们也可以在 Podfile 中添加一段脚本，自动处理这一情况：

```ruby
# Podfile
post_install do |installer|
   project_path = './AdaEmbedFramework.xcodeproj'
   project = Xcodeproj::Project.open(project_path)
   project.targets.each do |target|
    puts target
     if target.name == "AdaEmbedFramework"
         phase = target.shell_script_build_phases.find { |bp| bp.name == '[CP] Copy Pods Resources' }
         if !phase.nil?
            phase.input_paths.push('${TARGET_BUILD_DIR}/${UNLOCALIZED_RESOURCES_FOLDER_PATH}/Assets.car')
            phase.output_paths.delete('${TARGET_BUILD_DIR}/${UNLOCALIZED_RESOURCES_FOLDER_PATH}/Assets.car')
         end
     end
   end
   project.save(project_path)
end
```

> 虽然...解决了吧，但感觉还是有点治标不治本

## 在主工程 Build Phase 中增加 "Copy files" 配置

* 增加 “Copy Files”
* 将 xcassets 拖入配置中

这样工程在编译时，就不会从 xcassets 创建 `Access.car`，而是通过 cocoapods 将 xcassets 中的文件拷贝到主工程中，再从主工程中生成 `Access.car`，这样就不会有文件冲突。

# 最佳实践

最佳解决方案当然是在配置我们封装的 lib 时，使用 cocoapods 的 [resource_bundles](https://guides.cocoapods.org/syntax/podspec.html#resource_bundles)。

> 影响：这中做法会将资源文件导入到一个新的 bundle 中，在读取文件时，需要增加 bundle 参数。

# 小结

根据最优解可以看出，我们使用 cocoapods 封装自己的库时，如果它包含了资源文件，最好是以 module 内的 bundle 的方式添加，这样才能保证代码有较高的兼容性。


# 参考链接

* [https://dev.to/kylefoo/xcode-12-new-build-system-warns-multiple-commands-produce-assets-car-56im](https://dev.to/kylefoo/xcode-12-new-build-system-warns-multiple-commands-produce-assets-car-56im)
* [https://www.jianshu.com/p/1e46bf6c48eb](https://www.jianshu.com/p/1e46bf6c48eb)
* [https://developer.apple.com/documentation/xcode-release-notes/build-system-release-notes-for-xcode-10](https://developer.apple.com/documentation/xcode-release-notes/build-system-release-notes-for-xcode-10)
