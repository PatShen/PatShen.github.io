---
layout: post
title: Swift泛型的一种使用方式
tag: iOS, Swift, Genrics

---

* TOC
{:toc}

# UIKit

在 UIKit 中，我们可以通过以下步骤，实现一个类似系统 UIAlertController 的模态视图效果：

* 使用 `present(_:animated:completion:)` 函数
* 设置 `modalPresentationStyle = .custom`
* 设置 presetedViewController 的背景色为透明或半透明，可看到下层视图
* 通过 `modalTransitionStyle` 属性设置系统自带的动画（可选）

# SwiftUI

SwiftUI 也可以实现类似的效果，我们需要用到 fullScreenCover 这个方法

```Swift
content
  .fullScreenCover(isPresented: Binding<Bool>) {
    // 可以在内部实现自定义动画
    CustomerView()
  }
  .transaction { transcation in
    // 如果实现了自定义动画，为了避免其与系统自带动画冲突，我们可以在这里将系统动画禁用
    // 如果要直接用系统定义的动画，这一步可去掉
    transcation.disablesAnimations = true
  }
```

通过以上方法，我们可以为自定义的模态视图增加淡入淡出或其他自定义动画，自定义动画方面， 在 SwiftUI 中实现起来会比在 UIKit 中更加方便。

# 参考链接

* https://stackoverflow.com/questions/69712759/swiftui-fullscreencover-with-no-animation
* https://stackoverflow.com/questions/64301041/swiftui-translucent-background-for-fullscreencover
