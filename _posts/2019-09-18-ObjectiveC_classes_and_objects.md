---
layout: post
title: Objective-C 的类与对象
tag: Objective-C,iOS

---

* TOC 
{:toc}

本文主要探究类与对象的基础知识

# 方法
Objective-C 中有两种类型的方法：

``` objc
@interface AClass : NSObject 
// 类方法
+ (void) classMethod;
// 实例方法
- (void) instanceMethod;
@end
```

`类方法`又称作`静态方法`，可以不用创建对象来调用；而`实例方法`必须通过实例对象调用；

Objective-C 中的方法只要在 @interface 中声明，都认为是公有的；它没有绝对私有的方法，只能将方法隐藏；

隐藏方法的方式：

* 在 @implementation 中声明
* Category
* Extension

# 变量

苹果推荐使用 `@property` 来声明成员变量，作为类的属性；被声明的成员变量会在类的内部自动创建 `getter` 和 `setter` 方法，前者用于获取该属性，后者用于修改这个属性；

属性有两种修饰方式，一种是修饰 `getter` 和 `setter` 方法的原子性，另一种是设置读写属性；

## 原子性（默认值为 atomic）

* atomic : 保证属性在读写操作的原子性，它修饰的属性在读写操作完成后一定还是一个完整的属性；也就是说，它能保证读写操作的线程安全，但不能保证整个类的线程安全；
* nonatomic : 非原子性，因此在普遍情况下，用它修饰的属性在读写时会更快；

> 1.如果想要保证多线程下属性赋值的安全性，需要借助其他手段来实现；
> 
> 2.Swift 中默认为 atomic，且无法修改；如果一个类在 OC 中定义，它的属性在 Swift 中运行时，会被修饰为 `atomic`

参考链接

https://www.jianshu.com/p/7288eacbb1a2
https://www.jianshu.com/p/66b77270e363
https://stackoverflow.com/questions/588866/whats-the-difference-between-the-atomic-and-nonatomic-attributes
https://medium.com/@YogevSitton/atomic-vs-non-atomic-properties-crash-course-d11c23f4366c

## 读写（默认值为 readwrite assign）

* readwrite : 可读写；
* readonly : 只读，只会生成 getter
* assign : 赋值；
* retain : MRC 下的持有，setter 方法将传入参数先保留，再赋值，传入参数的 retain count 会+1; ARC 下也能用，但不建议；
* strong : ARC 独有，强引用，除非引用它的对象被释放，否则被强引用的对象将不会被释放；
* weak : ARC 独有，弱引用，被它修饰的属性遵循自身的释放流程，与引用它的对象释放与否无关；
* copy : 拷贝，setter 方法将传入对象复制一份；

同时，我们还可以使用自己定义 accessor 的名字：

```objc
@property (getter=isFinished) BOOL finished;
```
这种情况下，编译器生成的 getter 方法名为 isFinished，而不是 finished。

## @synthesize 和 @dynamic

* 系统默认会将属性 synthesize，生成 setter 和 getter 方法；
* 可读写(readwrite)属性实现了自己的 getter 和 setter；
* 只读(readonly)属性实现了自己的 getter；
* 使用 @dynamic，显式表示不希望编译器生成 getter 和 setter （例如 CoreData 中的对象）；
* Protocol 中定义的属性，编译器不会自动 synthesize，需要手动写；
* 当重载父类中的属性时，也必须手动写 synthesize；

# 类的扩展

## 继承

创建子类，继承父类的属性、方法等；

## Protocol

协议，类似 C++ 中的多重继承，可以让多个不同的类实现类似的接口；

## Category 

* 可以不知晓某个类的源码、无需继承，来实现扩展其功能的效果；使用场景为将方法模块化，分别在不同的文件中实现；
* 在使用 Category 时需要注意的一点是，如果有多个命名 Category 均实现了同一个方法（即出现了命名冲突），那么这些方法在运行时只有一个会被调用，具体哪个会被调用是不确定的。因此在给已有的类（特别是 Cocoa 类）添加 Category 时，推荐的函数命名方法是加上前缀

```objc
@interface NSString (ABCEmpty)

- (BOOL)abc_isEmpty;

@end
```

## Extention

* 可以认为是匿名的 Category；
* 必须知晓类的源码；
* Extension 声明的方法必须在类的主 @implementation 区间内实现，可以避免使用有名 Category 带来的多个不必要的 implementation 段；
* Extension 可以在类中直接添加新的属性和实例变量，Category 需要使用其他方式才可以

### 给已有的类添加属性

Extension 可以给类添加属性，编译器会自动生成 getter，setter 和 ivar。 Category 并不支持这些。如果使用 Category 的话，类似下面这样：

```objc
@interface XYZPerson (UDID)
@property (readwrite) NSString *uniqueIdentifier;
@end

@implementation XYZPerson (UDID)
...
@end
```

尽管编译可以通过，但是当真正使用 uniqueIdentifier 时直接会导致程序崩溃。

如果我们手动去 synthesize 呢？像下面这样：

```objc
@implementation XYZPerson (UDID)
@synthesize uniqueIdentifier;
...
@end
```

然而这样做的话，代码直接报编译错误了：

```
@synthesize not allowed in a category's implementation
```

经过查阅网上资料，我们可以用 OC 的 Runtime 机制来实现这样的效果

```objc

@implementation XYZPerson (UDID)
@dynamic uniqueIdentifier;

- (void)setUniqueIdentifier:(NSString*)identifier {
     objc_setAssociatedObject(self, @selector(uniqueIdentifier), identifier, OBJC_ASSOCIATION_RETAIN_NONATOMIC);
}

- (NSString*)uniqueIdentifier {
    return objc_getAssociatedObject(self, @selector(uniqueIdentifier));
}
...
@end
```

# 类的导入

* \#include: 是C/C++导入头文件的关键字
* \#import: 是Objective-C导入头文件的关键字；头文件会自动只导入一次，不会重复导入；
* @class: 告诉编译器需要知道某个类的声明，可以解决头文件的相互包含问题；使用时一般在 interface 中声明，需要在 .m 文件中引用该头文件；

## 类的初始化

在 OC 中绝大部分类都继承自 `NSObject`，它有两个非常特殊的类方法 `load` 和 `initilize`，用于类的初始化

### +load

`load` 是在被添加到 `runtime` 时开始执行，父类最先执行，然后是子类，最后是 `Category`。又因为是直接获取函数指针来执行，不会像 `objc_msgSend` 一样会有方法查找的过程。

### +initilize

`initialize` 最终是通过 `objc_msgSend` 来执行的，`objc_msgSend` 会执行一系列方法查找，并且 `Category` 的方法会覆盖类中的方法。


|| +load | +initialize |
|------ |------ | --- |
调用时机 | 被添加到 runtime 时 |收到第一条消息前，可能永远不调用
调用顺序| 父类->子类->分类 |父类->子类
调用次数| 1次 |多次
是否需要显式调用父类实现| 否| 否
是否沿用父类的实现| 否 |是
分类中的实现 |类和分类都执行 |覆盖类中的方法，只执行分类的实现

参考链接

https://www.jianshu.com/p/872447c6dc3f