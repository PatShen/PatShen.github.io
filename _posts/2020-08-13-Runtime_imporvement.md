---
layout: post
title: Objctive-C Runtime 改良版
tag: Objective-C,runtime

---

* TOC
{:toc}

# Runtime

之前有写过一篇关于 Runtime 的 [文章](https://patshen.github.io/2019/09/26/ObjectiveC_runtime.html)，感觉有点...不太好理解，这篇就来简化一下。

## runtime是什么？

在编译、链接之后，负责执行 OC 代码；

## 交互

* OC 的几乎所有方法，调用方法时，系统会通过消息的方式与目标交互；NSObject 的 isKindOfClass 等方法，在运行时判断类型；
* Runtime 接口；

### 消息传递

* 每当初始化一个类的实例，它会有一个 isa 指针，用来指向它的类结构，使得这个类可以访问它本身和它的父类（super class）；
* 调度表，用来将 selector 和具体的方法关联；

大致流程：

调用方法 -> isa -> 类 -> 调度表查询 selector（先查子类，没有就查父类，递归） -> 找到对应的方法

缓存机制：按类缓存；

## runtime 能干什么？

利用动态方法解析和消息转发，可以让一个类执行一个它自己没有实现的方法时，转移到另一个实现了这个方法的类中；

### 动态方法解析和消息转发

![RunLoop内部逻辑](/assets/img/20200813runtime/messaging.png)

当代码执行方法时，例如`[receiver message]`，执行过程如上图所示：

1. 系统会先调用 `+ (BOOL)resolveInstanceMethod:(SEL)sel` 方法，如果当前的类实现了这个方法，则返回 `YES`，否则返回 `NO`；返回前者就直接执行语句了。
2. 如果上一步返回了 `NO`，会调用 `- (id)forwardingTargetForSelector:(SEL)aSelector`，在这里我们可以自己返回需要执行这个方法的类；
3. 如果2返回了具体对象，系统就会再次经历上面的过程去执行方法；
4. 如果2返回了 nil 或 self，会由当前类或它的父类执行 `- (void)forwardInvocation:(NSInvocation *)anInvocation`，如果族群没有一个类实现这个方法，就会崩溃；

> 以上，1和2是动态方法解析的过程，3和4是消息转发的过程；

### 多重继承

上面的第三步，在这种情况下我们可以理解为新的类“继承”了需要调用的方法，而且可以转发给多个类去执行，所以我们可以理解为实现了类似“多重继承”的效果；

### 声明属性

我们知道，类可以声明属性，属性的赋值和读取实际上是通过 `set/get` 方法实现的，因此我们也可以在运行时动态的为对象增加新的属性

例如对于 ClassA，有这样一个分类，定义了一个属性：

```Objc
@interface ClassA (Category) {
    @property (nonatomic, assign) Int length;
}

```

那么实现属性的读写方法可以通过以下方式：

```Objc
static const void *kLength = "kLength";

@implementation ClassA (Category) {
    - (void)setLength:(Int)length {
        objc_setAssociatedObject(self, kLength, @(length), OBJC_ASSOCIATION_ASSIGN);
    }
    
    - (Int)length {
        return objc_getAssociatedObject(self, kLength);
    }
}
```

# 参考文献/链接

* [我之前整理的](https://patshen.github.io/2019/09/26/ObjectiveC_runtime.html)
* [iOS runtime消息转发机制等](https://www.jianshu.com/p/1d1fc99460ad)