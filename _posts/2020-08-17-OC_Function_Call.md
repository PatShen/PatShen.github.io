---
layout: post
title: Objctive-C 方法调用
tag: Objective-C,runtime

---

* TOC
{:toc}

在之前的一篇文章中，我总结了 runtime 调用方法时消息转发的过程，中间有一步提到，类内部是通过调度表查询 selector，再找到对应方法来执行的。那么 OBJC 类是如何通过 selector 找到方法的呢？本文将对这部分内容展开描述；

在了解具体原理之前，我们还需要先了解几个概念：`SEL`，`IMP`，`Method`

> 源码下载地址：[源码](https://opensource.apple.com/tarballs/objc4/)

# 几个概念

## SEL

在源码中找到 `objc.h` 文件，能够发现 `SEL` 的声明：

```Objc
/// An opaque type that represents a method selector.
typedef struct objc_selector *SEL;
```

这里的 `objc_selector` 是什么，[这里](https://blog.csdn.net/jeffasd/article/details/52084639)有篇文章有具体说明；在 iOS 中，我们可以将 `SEL` 理解为一个字符串，与方法名成一一对应的关系；

## IMP

```Objc
/// A pointer to the function of a method implementation. 
#if !OBJC_OLD_DISPATCH_PROTOTYPES
typedef void (*IMP)(void /* id, SEL, ... */ ); 
#else
typedef id _Nullable (*IMP)(id _Nonnull, SEL _Nonnull, ...); 
#endif
```

声明包含了一个无参数、无返回值的情况，和一个有参数、有返回值的情况；

它实际上是一个函数指针，指向方法实现的首地址，runtime 方法调用最后一步就是执行 imp；如果我们能够直接获取 IMP 指针，就可以绕过消息发送机制，从而让方法调用更迅速；

在实际应用中，我们可以通过类似下面的方式调用方法：

```Objc
// 有返回值
- (void)callIMP {
    NSString* text = "";
    SEL selector = NSSelectorFromString(@"functionName");
    if ([self respondsToSelector:selector]) {
        IMP imp = [self methodForSelector:selector];
        NSString* (*func)(id, SEL) = (void*)imp;
        text = func(self, selector);
    }
    NSLog(@"text: %@",text);
}

```

```Objc
// 无返回值
- (void)callIMP {
    SEL selector = NSSelectorFromString(@"functionName");
    if ([self respondsToSelector:selector]) {
        IMP imp = [self methodForSelector:selector];
        void (*func)(id, SEL) = (void*)imp;
        func(self, selector);
    }
}
```

一般我们会采用 `# pragma GCC diagnostic ignored "-Wreceiver-is-weak"` 的方式消除方法调用的警告，现在我们能够通过 IMP 更优雅地实现它；

## method

在我下载的这个版本的源码中，并没有发现 `method` 的声明；但是在网上还是有很多先行者给出了他们的答案：

```Objc
/// An opaque type that represents a method in a class definition.
typedef struct objc_method *Method;

struct objc_method {
    SEL method_name                                          OBJC2_UNAVAILABLE;
    char *method_types                                       OBJC2_UNAVAILABLE;
    IMP method_imp                                           OBJC2_UNAVAILABLE;
}
```

看起来这个 API 已经被弃用了，不过我们仍然能通过这份声明发现 `method` 与 `SEL` 和 `IMP` 的联系：即系统是通过 `method` 建立 `SEL` 和 `IMP` 的联系，从而通过 `SEL` 找到 `IMP` 并执行的。


# 总结

通过本文，再加上我[之前的文章](https://patshen.github.io/2020/08/13/Runtime_imporvement.html)里描述的，我们能够很自然的得出 OC 方法调用的大致流程：

```
调用方法 -> isa -> 类 -> 调度表查询 selector（先查子类，没有就查父类，递归） -> IMP -> 执行
```

# 参考链接

* [深入理解 Objective-C 的方法调用流程](https://www.jianshu.com/p/114782a909f9)
* [OC 中 objc_selector 结构体详解](https://blog.csdn.net/jeffasd/article/details/52084639)