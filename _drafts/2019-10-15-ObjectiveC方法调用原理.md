---
layout: post
title: Objective-C 方法调用原理
tag: Objective-C

---

* TOC
{:toc}

本文主要阐述 Objective-C 语言的方法调用原理，以及理解之后能做什么。

# 概述

我们知道，Objective-C 语言的方法调用是通过发送消息来实现的，在苹果开源的 runtime 代码中定义为：

```objc
OBJC_EXPORT id _Nullable objc_msgSend(id _Nullable self, SEL _Nonnull op, ...) OBJC_AVAILABLE(10.0, 2.0, 9.0, 1.0, 2.0);
```

详细信息可以查看[这里](https://patshen.github.io/2019/09/26/ObjectiveC_runtime.html#objc_msgsend-函数)

下面我们来针对 `objc_msgSend` 中的各个参数及返回值做逐一阐述

> 本文编写过程中参考的 `runtime` 源码版本为 `756.2`，附[下载地址](https://opensource.apple.com/tarballs/objc4/)

# 详细介绍

下面我们来详细介绍与之相关的几个基本类型

## objc_object

```objc
struct objc_object {
private:
    isa_t isa;

public:

    // ISA() assumes this is NOT a tagged pointer object
    Class ISA();

    // getIsa() allows this to be a tagged pointer object
    Class getIsa();
    
    // 以下省略...
}
```

`objc_object` 结构体中包含一个 `isa` 指针，可以理解为英文的 "is a"，它使对象可以访问它的类以及它的所有超类。

## objc_class

```objc
struct objc_class : objc_object {
    // Class ISA;
    Class superclass;
    cache_t cache;             // formerly cache pointer and vtable
    class_data_bits_t bits;    // class_rw_t * plus custom rr/alloc flags

    class_rw_t *data() { 
        return bits.data();
    }
    
    // 以下省略...
}
```

`objc_class` 继承自 `objc_object`，那么 `objc_class` 也拥有一个 isa 指针。

## Class

`Class` 其实是一个指向 `objc_class` 的指针：

```objc
/// An opaque type that represents an Objective-C class.
typedef struct objc_class *Class;
```

一个对象的 isa 指针所指向的类，就表明它是这个类的对象。那么对于 Class 来说，它的 isa 指向的类，就是我们所知的 `meta class`，类对象所属类型就叫做`元类`。

当我们发出一个类似 `[NSObject alloc]` 的消息时，实际上是把这个消息发给了一个类对象（Class Object），这个类对象必须是一个元类的实例，而这个元类同时也是一个根元类 (root meta class) 的实例。所有的元类最终都指向根元类为其超类。所有的元类的方法列表都有能够响应消息的类方法。

所以当 `[NSObject alloc]` 这条消息发给类对象的时候，`objc_msgSend()` 会去它的元类里面去查找能够响应消息的方法，如果找到了，然后对这个类对象执行方法调用。

下图实线是 `superclass` 指针，虚线是 `isa` 指针。有趣的是根元类的超类是 `NSObject`，而 `isa` 指向了自己，而 `NSObject` 的超类为 `nil`，也就是它没有超类。

可以看到运行时一个类还关联了它的超类指针，类名，成员变量，方法，缓存，还有附属的协议。

![class](/assets/img/objc方法调用原理/class-diagram.jpg)

## id

`objc_msgSend` 的第一个参数类型及返回值都是 `id`，是我们常用的一种可以转换为任意类型的数据类型，它的定义如下：

```objc
/// A pointer to an instance of a class.
typedef struct objc_object *id;
```

这里可以看出，它是一个指向类实例的指针；同时它也是一个结构体指针，因此在使用时变量不需要加 `*`。

## SEL

`SEL` 的定义如下：

```objc
/// An opaque type that represents a method selector.
typedef struct objc_selector *SEL;
```

源码中无法直接确认 `objc_selector` 的定义，但我们可以从官方文档中得知，它是 `selector` 在 `Objective-C` 中的表示类型（ `Swift` 中是`Selector` 类）。`selector` 是方法选择器，可以理解为区分方法的 ID。

## IMP

`IMP` 的定义如下：

```objc
/// A pointer to the function of a method implementation. 
#if !OBJC_OLD_DISPATCH_PROTOTYPES
typedef void (*IMP)(void /* id, SEL, ... */ ); 
#else
typedef id _Nullable (*IMP)(id _Nonnull, SEL _Nonnull, ...); 
#endif
```

它可以理解为是一个函数指针，指向了函数实现的代码。当你发起一个 ObjC 消息之后，最终它会执行的那段代码，就是由这个函数指针指定的。

## Method

`Method` 的定义如下：

```objc
/** objc-private.h **/
typedef struct method_t *Method;


/** objc-runtime-new.h **/
struct method_t {
    SEL name;
    const char *types;
    MethodListIMP imp;

    struct SortBySELAddress :
        public std::binary_function<const method_t&,
                                    const method_t&, bool>
    {
        bool operator() (const method_t& lhs,
                         const method_t& rhs)
        { return lhs.name < rhs.name; }
    };
};

```

我们可以认为 Method = SEL + IMP + method_types，相当于在 `SEL` 和 `IMP` 之间建立了一个映射。

# 方法调用

理解了以上几个基本类型之后，我们就能更好理解方法调用的过程了。

当我们进行函数调用时，像下面这种写法：

```objc
[receiver message]
```

编译器会将其转换为 `objc_msgSend`，下面两种情况分别为不带参数和带参数：

```objc
// 不带参数
objc_msgSend(receiver, selector)

// 带参数
objc_msgSend(reciever, selector, arg1, arg2, ...)
```


# 参考链接

* [objective-c-runtime](http://yulingtianxia.com/blog/2014/11/05/objective-c-runtime/)
* [深入理解Objective-C：方法调用](https://yangjie2.github.io/2018/10/15/深入理解Objective-C：方法调用/)

https://www.jianshu.com/p/137029cc6056
https://www.jianshu.com/p/9a5416152271