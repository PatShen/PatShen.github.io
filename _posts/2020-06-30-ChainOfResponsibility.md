---
layout: post
title: iOS 设计模式-责任链
tag: Swift,Design Patterns

---

* TOC
{:toc}

# 定义

引用维基百科的定义：
> 责任链模式在面向对象程式设计里是一种软件设计模式，它包含了一些命令对象和一系列的处理对象。每一个处理对象决定它能处理哪些命令对象，它也知道如何将它不能处理的命令对象传递给该链中的下一个处理对象。该模式还描述了往该处理链的末尾添加新的处理对象的方法。

这个定义乍一眼看起来有点难懂，我们暂且放一放，后续通过例子可以更好的理解它。

# 作用

责任链的工作过程可以简单的通过下图体现出来：

![图1](#/assets/img/20200630chainofresposiblity/1.png)

先由事件的发起者发起一个事务，由责任链负责将其处理完成并将结果反馈给发起者。对于发起者来说，责任链内部的成员、顺序、结果都是不可见的，这大大降低了二者之间的耦合度，它只需要获取最终的结果即可。

![图2](#/assets/img/20200630chainofresposiblity/2.png)

在责任链的内部，可以有多个实体对外部的请求做处理，如果某个实体无法处理事务，那么它将会将事务传递给下一个实体。

> 理想情况下，只要某个实体无法完全处理事务，它就应该终止责任链传递并将结果反馈；
但在实际使用的过程中，这种情况并不多见，我们可以适当做一些变通；


# 优缺点
根据以上阐述，我们能够很清楚地知道这种设计模式的优点：

**优点**

* 能够解耦事务的发起者和处理者；
* 链内实体可以灵活地进行增、删、排序；
* 链内实体指责单一，符合单一指责原则；

**缺点**也比较明显：

* 事务可能不会被任何一个实体处理；
* 责任链内可能引起循环引用；

# 场景

* 需要按照一定顺序执行多个事件处理逻辑时；
* 需要动态改变、或经常修改多个事件处理逻辑的个数、顺序时；

# 举例

假如有个提交用户信息表单的需求，需要判断每一个选项都有值后，再进行提交

我们先定义一个协议

```Swift
/// 责任链协议
protocol Chain {
    /// 定义是否合理的方法，由具体的责任链实体实现
    func isValidate() -> Bool
    /// 定义id，区分不同的责任链，用于提示等
    func getIdentifier() -> String
    /// 获取下一个责任链实体
    func getNextChain() -> Chain?
    /// 实际操作过程
    func request(_ completion: (_ error: NSError?) -> (Void))
}
/// 默认实现
extension Chain {
    func request(_ completion: (_ error: NSError?) -> (Void)) {
        if !self.isValidate() {
            // 不满足条件，抛出错误
            let msg = "error: \(self.getIdentifier()) is empty"
            let error = NSError.init(domain: "", code: 1, userInfo: ["msg" : msg])
            completion(error)
            return
        }
        if let c = self.getNextChain() {
            c.request { completion($0) }
        } else {
            // 此时表示责任链执行完成
            let error = NSError.init(domain: "", code: 0, userInfo: ["msg" : "No error, and this is the last Chain"])
            completion(error)
        }
    }
}
```

再定义一些责任链实体，用来处理不同的逻辑：

```Swift
/// 用户名
class NameChain {
    var chain: Chain?
}
extension NameChain: Chain {
    func isValidate() -> Bool {
        // 此处省略一些判断逻辑
        return true
    }
    func getNextChain() -> Chain? {
        return self.chain
    }
    func getIdentifier() -> String {
        return "name"
    }
}

/// 手机号
class PhoneChain {
    var chain: Chain?
}
extension PhoneChain: Chain {
    func isValidate() -> Bool {
        // 此处省略一些判断逻辑
        return true
    }
    func getNextChain() -> Chain? {
        return self.chain
    }
    func getIdentifier() -> String {
        return "phone"
    }
}

/// 头部实体
class Head {
    var chain: Chain?
}
extension Head: Chain {
    func isValidate() -> Bool {
        return true
    }
    func getNextChain() -> Chain? {
        return self.chain
    }
    func getIdentifier() -> String {
        return "Head"
    }
}
```
> 可能有人注意到，以上实体都没有实现 request 方法，因为 Swift 语言的特性在协议的扩展中，我们为它默认实现了一套逻辑，因此除非有特殊需要，否则在实体类中无需再次实现这个方法。
> 
> 我们还可以根据实际情况新增其他责任链实体，例如性别、地址等等；

最后我们再将它们调用：

```Swift
let head = Head.init()
let name = NameChain.init()
let phone = PhoneChain.init()

head.chain = name
name.chain = phone

head.request {
    if let error = $0 {
        if (error.code == 0) {
            // 成功，执行业务逻辑
        }
        else {
            // 失败，执行业务逻辑
        }
        print(error)
    } else {
        // 此处省略业务逻辑
        print("no error")
    }
}
```

# 补充说明

本文中的代码完整可以在 [这里](https://github.com/PatShen/ChainOfResposibilityDemo) 找到，采用的工具版本分别是 `XCode 11.5`，`Swift 5.1`

# 参考链接
* [责任链模式（维基百科）](https://zh.wikipedia.org/wiki/%E8%B4%A3%E4%BB%BB%E9%93%BE%E6%A8%A1%E5%BC%8F)
* [iOS设计模式-责任链
](http://jackliu17.github.io/2016/06/06/iOS%E8%AE%BE%E8%AE%A1%E6%A8%A1%E5%BC%8F-%E8%B4%A3%E4%BB%BB%E9%93%BE/)
* [责任链模式：Chain of Responsibility](https://juejin.im/post/5d63cc41e51d453b730b0f63)
