---
layout: post
title: Objective-C KVC
tag: objective-c,kvc

---

* TOC
{:toc}

# 关于 KVC

## 概念

KVC 即 Key-Value Coding，键值编码。它是一种可以只通过属性名称字符串`间接`访问对象属性和关系的机制；支持 KVC 的对象可以通过 `NSKeyValueCoding` 协议的方法对属性进行间接读取。

KVC 是许多其他 Cocoa 技术的基础，例如 `Key-Value Observing(KVO)`、`Cocoa bindings`、`Core Data` 和 `AppleScript-ability`。某些情况下 KVC 还能帮助我们简化代码。

## 对于支持 KVC 的对象我们能做什么

所有继承自 `NSObject` 的对象都支持 KVC，不仅如此，这些对象都默认实现了 `NSKeyValueCoding` 协议。它们能通过消息接口 (messaging interface) 做到以下这些事：

* 获取对象的属性
* 操作集合属性（例如 NSArray）
* 在集合对象上调用集合运算符
* 访问非对象属性
* 通过 keypath 访问属性


## 让自定义对象支持 KVC

为了让对象支持 KVC，我们必须实现一些 `NSKeyValueCoding` 协议的方法，比如让 `valueForKey` 作为 getter 方法、让 `setValue:forKey:` 作为 setter 方法等。

就像之前我所提到的，`NSObject` 及其子类均已实现了以上协议，所以我们的自定义类只要继承自 `NSObject` 就默认支持 KVC。

## KVC 在 Swift 中的使用

Swift 能支持 KVC 吗？当然是可以的，这需要 Swift 对象继承自 `NSObject`。这种场景可能会较多的出现在 OC & Swift 混编的项目中。在纯 Swift 项目中，因为 Swift 语言的一些特性，我们不再必须使用 KVC 就能实现类似的效果。*例如，由于所有Swift属性都是对象，因此您永远不会对默认实现对非对象属性的特殊处理。*

# KVC 基础

## 访问对象的属性

访问对象属性的方法有以下几种：

**Get 方法**

* valueForKey:
* valueForKeyPath:
* dictionaryWithValuesForKeys:

**Set 方法**

* setValue:forKey:
* setValue:forKeyPath:
* setValuesForKeysWithDictionary:

这里有几点需要单独解释一下：

### key path

`key path` 是一个由 "." 连接的多段 key 组成的字符串。例如 "person.address.street" 就可以访问“某人在所有的地址中街道的值”。其中 person、address 表示的对象都支持 KVC。

### 获取一对多关系的属性

当我们通过 Get 方法获取到的是一个一对多关系的属性时，它的返回的值将会是一个集合，其中包含一对多键右侧的键的所有值。

> 例如我们通过 key path `transactions.payee` 获取到的值是一个数组，这个数组将会包含所有属于 `transactions` 的 `payee` 对象。

### 通过 Get 方法获得 nil

在集合对象（NSArray、NSSet、NSDictionary）中，无法包含 `nil` 对象。但是我们可以使用 `NSNull` 来代替它，`NSNull` 提供了一个可以表示 `nil` 值的实例。在 `dictionaryWithValuesForKeys:` 和 `setValuesForKeysWithDictionary:` 的相关实现中会用到。

### 通过 set 方法设置 nil 

在默认情况下，当我们尝试将非对象属性设置为 nil 时，KVC 将会调用 `setNilValueForKey:` 的消息来调用对应的方法，而默认的 `setNilValueForKey:` 方法将会抛出一个 `NSInvalidArgumentException` 异常，我们可以重写这个方法来实现一个默认值的效果，这点我们会在后面讲到。

## 访问集合属性

一般情况下，我们可以通过 `valueForKey:` 和 `setValue:forKey:` 两个方法来获取或设置集合对象，但是这样获取或得到的对象都是不可变的，如果我们想要操作可变数组、元组（set）、有序元组（SortedSet），可以用一下几个方法：

* NSMuableArray: `mutableArrayValueForKey:` 和 `mutableArrayValueForKeyPath:`
* NSMutableSet: `mutableSetValueForKey:` 和 `mutableSetValueForKeyPath:`
* NSMutableOrderedSet: `mutableOrderedSetValueForKey:` 和 `mutableOrderedSetValueForKeyPath:`

在实际的工作中，苹果更倾向于使用这种方式来改变属性；关于这一点 KVO 会给我们答案。

## 使用集合运算符

除了可以通过字符串直接获取属性之外，KVC 还提供了一些便捷的操作来实现特定的功能，我们可以在 `key path` 中添加一些以 `@` 开头的标识来表示这些运算符。

集合运算符一共有三种：简单集合运算符、数组运算符和嵌套运算符

在说明这些运算符之前，我们先来做一些必要的定义

下面定义了 BankAccount 和 Transaction 类

```objc
@interface BankAccount : NSObject

@property (nonatomic) NSNumber* currentBalance;

@property (nonatomic) Person* owner;

@property (nonatomic) NSArray<Transcation* >* transcations;

@end
```

```objc
@interface Transaction : NSObject

@property (nonatomic) NSString* payee;

@property (nonatomic) NSNumber* amount;

@property (nonatomic) NSDate* date;

@end
```

假设有以下这些数据：

|`payee` Value|`amount` values formatted as currency|`date` values formatted as month day, year|
|-------------|----------|--------|
|Green Power|$120.00|Dec 1, 2015|
|Green Power|$150.00|Jan 1, 2016|
|Green Power|$170.00|Feb 1, 2016|
|Car Loan|$205.00|Jan 15, 2016|
|Car Loan|$205.00|Feb 15, 2016|
|Car Loan|$205.00|Mar 15, 2016|
|General Cable|$120.00|Dec 1, 2015|
|General Cable|$155.00|Jan 1, 2016|
|General Cable|$120.00|Feb 1, 2016|
|Mortgage|$1,025.00|Jan 15, 2016|
|Mortgage|$1,025.00|Feb 15, 2016|
|Mortgage|$1,025.00|Mar 15, 2016|
|Animal Hospital|$600.00|Jul 15, 2016|

### 简单集合运算符

#### @avg 

会先将该运算符右边 key path 对应的所有属性转换成 `double`（ nil 将会被转换成 0 ），再计算它们的平均值，结果会返回一个 `NSNumber` 对象：

```objc
NSNumber *transactionAverage = [self.transactions valueForKeyPath:@"@avg.amount"];

// 结果为 456.54
```

#### @count 

计算该运算符右边 key path 对应的所有集合类型属性的元素的数量，最后返回一个 `NSNumber` 对象；例如下面的例子会返回 `Transcation` 对象中所有 `transcations` 的数量：

```objc
NSNumber *numberOfTransactions = [self.transactions valueForKeyPath:@"@count"];

// 结果为 13
```

#### @max 

使用 `compare:` 方法计算该运算符右边 key path 对应的所有属性的最大值，所以此处的 key path 对应的属性必须实现 `compare:` 方法：

```objc
NSDate *latestDate = [self.transactions valueForKeyPath:@"@max.date"];

// 结果为 Jul 15, 2016
```

#### @min 

该方法的计算过程和 @max 类似，最终返回最小值：

```objc
NSDate *earliestDate = [self.transactions valueForKeyPath:@"@min.date"];

// 结果为 Dec 1, 2015
```

#### @sum

这个方法的计算过程和 @count 类似，最终返回所有数之和：

```objc
NSNumber *amountSum = [self.transactions valueForKeyPath:@"@sum.amount"];

// 结果为 5,935.00
```

### 数组运算符

数组运算符使valueForKeyPath：返回一个对象数组，该对象数组与右键路径指示的一组特定对象相对应。

#### @distinctUnionOfObjects

去重

```objc
NSArray *distinctPayees = [self.transactions valueForKeyPath:@"@distinctUnionOfObjects.payee"];

// 结果为 [Car Loan, General Cable, Animal Hospital, Green Power, Mortgage]
```

#### @unionOfObjects

不去重

```objc
NSArray *payees = [self.transactions valueForKeyPath:@"@unionOfObjects.payee"];

// 结果为 [Green Power, Green Power, Green Power, Car Loan, Car Loan, Car Loan, General Cable, General Cable, General Cable, Mortgage, Mortgage, Mortgage, Animal Hospital.]
```

### 嵌套运算符

嵌套运算符对嵌套集合进行操作，其中集合本身的每个条目都包含一个集合。

假设现在有下面的数据：

```objc
NSArray* moreTransactions = @[<# transaction data #>];
NSArray* arrayOfArrays = @[self.transactions, moreTransactions];
```

|`payee` values|`amount` values formatted as currency|`date` values formatted as month day, year|
|-----|-----|-----|
|General Cable - Cottage|$120.00|Dec 18, 2015|
|General Cable - Cottage|$155.00|Jan 9, 2016|
|General Cable - Cottage|$120.00|Dec 1, 2016|
|Second Mortgage|$1,250.00|Nov 15, 2016|
|Second Mortgage|$1,250.00|Sep 20, 2016|
|Second Mortgage|$1,250.00|Feb 12, 2016|
|Hobby Shop|$600.00|Jun 14, 2016|

#### @distinctUnionOfArrays

创建并返回一个数组，将 key path 对应的元素添加进去，并做去重处理：

```objc
NSArray *collectedDistinctPayees = [arrayOfArrays valueForKeyPath:@"@distinctUnionOfArrays.payee"];

// 结果是 [Hobby Shop, Mortgage, Animal Hospital, Second Mortgage, Car Loan, General Cable - Cottage, General Cable, Green Power.]
```

#### @unionOfArrays

创建并返回一个数组，将所有 key path 对应的元素添加进去，不做去重处理：

```objc
NSArray *collectedPayees = [arrayOfArrays valueForKeyPath:@"@unionOfArrays.payee"];

// 结果是 [Green Power, Green Power, Green Power, Car Loan, Car Loan, Car Loan, General Cable, General Cable, General Cable, Mortgage, Mortgage, Mortgage, Animal Hospital, General Cable - Cottage, General Cable - Cottage, General Cable - Cottage, Second Mortgage, Second Mortgage, Second Mortgage, Hobby Shop.]
```

#### @distinctUnionOfSets

创建并返回一个 `NSSet` 对象，因为 `NSSet` 不存在相同的两个元素，所以它的结果和 @distinctUnionOfArrays 类似，都做了去重处理，只不过返回对象的类型不是 `NSArray` 而是 `NSSet`；

## 表示非对象的值

KVC 只能操作对象，在 Objective-C 中，需要将非对象转换成对象，才能通过 KVC 调用。

> 在 Swift 中，所有的属性都是对象，因此本节内容仅适用于 Objective-C 属性。

## 验证属性

验证属性是否合法，可以通过 `validateValue:forKey:error:` 或 `validateValue:forKeyPath:error:` 来实现，默认情况下，系统会到对象中查询是否有对应的 key 或 key path。

> 通常我们只需要在 Objective-C 中使用验证，而 Swift 因为是强类型的语言，在编译时就能判断类型是否正确，因此不需要额外的验证机制。


