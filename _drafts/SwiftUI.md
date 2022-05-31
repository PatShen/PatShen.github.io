

* TOC
{:toc}

> 尽管在 iOS 13 之后就可以使用 SwiftUI 了，但是我还是建议在最低支持 iOS 14 之后再考虑使用它。
> 其中一个原因是部分功能在 iOS 13 中无法直接使用。例如 `UICollectionView` 在 iOS 13 中没有对应的控件直接实现，我们只能通过 `VStack` 和 `ScrollView` 组合才能实现类似的效果。而直到 iOS 14 才能直接通过 `LazyHGrid` 和 `LazyVGrid` 实现 UICollectionView 的功能。

# 基本用法

苹果提供了一套非常详细的[官方文档](https://developer.apple.com/tutorials/swiftui)，通过文档我们可以从0开始一步一步的熟悉 SwiftUI。

## Stack

在 SwiftUI 中引入了一个新的容器，即 Stack，在 SwiftUI 中大部分的 UI 绘制都在 Stack 这个容器中进行，与之对应的，是 UIKit 中的 `addSubview`。Stack 分为 `HStack`、`VStack` 和 `ZStack` 三种类型。

`HStack`(Horizontal) 和` VStack`(Vertical) 都很好理解，比较特殊的是 `ZStack`。

我的理解，结合它的实际效果，它的命名来源于 3D 坐标系中的 `Z轴`，我们可以用它实现控件堆叠在一起的效果，在前面被`描述`的元素会出现在底部，以此类推。

官方有一个例子能够很清楚的描述这个效果：

![zstack](/assets/img/xxx.jpg)

## 一些有用的关键字

关键字|描述|例子
-----|---|-----
@State|You use the @State attribute to establish a source of truth for data in your app that you can modify from more than one view. SwiftUI manages the underlying storage and automatically updates views that depend on the value.|
@Published|An observable object needs to publish any changes to its data, so that its subscribers can pick up the change.|
@EnvironmentObject|环境变量，功能有点类似全局变量|
@StateObject|Use it to initialize a model object for a given property only once during the life time of the app. This is true when you use the attribute in an app instance, as shown here, as well as when you use it in a view.|
@Binding|类型是 Bindg<T> (范型).|

## 在 SwiftUI 中使用 UIKit 控件

* 实现 `UIViewControllerRepresentable` 协议，将自定义的 `UIViewController` 桥接到 SwiftUI
* 实现 `UIViewRepresentable` 协议，将自定义的 `UIView` 桥接到 SwiftUI
* 我们可以在 SwiftUI 中定义一个`Coordinator` 对象，去实现 UIKit 的协议

## 在 UIKit 中使用 SwiftUI 控件

* 可以参考[这篇文章](https://www.avanderlee.com/swiftui/integrating-swiftui-with-uikit/)


