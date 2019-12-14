# Article_Crawler

## 项目介绍
一个用于博客、咨询等网站文章爬取的爬虫框架。

## 项目文件夹结构
- config/ 配置文件目录
- crawlers/ 爬虫文件目录
- log/ 日志文件目录
- utils/ 工具类文件目录

## 爬虫说明
网站文章的爬取主要分为两步：
1. 从网站中获取所有文章的url
2. 根据文章url获取其标题、内容等数据

在第一步中，网站又分为两类：
1. 通过页码拼接实现分页的网站
2. 动态加载页面的网站

这两类网站需要通过不同的方式去获取其所有文章的url，
在配置文件的`mode`字段进行设定以便爬虫框架进行相应处理（pagination、dynamic loading）。

## 配置文件说明
### 通过页码拼接实现分页的网站
#### 说明
```ini
[网页名称]
mode=pagination
page_name=网页名称
page_url=网页url地址
page_pagination_url=分页部分的拼接地址
start_pagination_number=开始分页的页码
page_is_end=判断网页分页是否结束的方法（404|single page|xpath路径）
article_xpath=文章在HTML代码中的标签的xpath路径
article_url_xpath=文章url在HTML代码中的标签的xpath路径
start_article_number=文章在HTML代码中的标签的开始编号
end_article_number=文章在HTML代码中的标签的结束编号
article_number_gap=编号间隔
title_xpath=文章标题的xpath路径
content_xpath=文章内容的xpath路径
detail_splice_flag=爬取文章详情时，url是否需要拼接（true|false）
splice_base_url=拼接的基础url
```
`page_is_end`字段有三个选项：
1. 404（表示网页分页结束时，返回404错误）
2. single page（表示网页只有一页，无需分页，此时`page_pagination_url`字段可为空，
`start_pagination_number`字段的值必须大于1）
3. xpath路径（表示网页分页结束时，指定的xpath路径没有数据）

`detail_splice_flag`字段有两个选项：
1. true（表示爬取文章详情时，从网站获取的文章url需要与`splice_base_url`字段中的url进行拼接）
2. false（表示无需拼接）

例如网站http://me.tryblockchain.org

获取到的文章url为`bitcoin-blockchain-misunderstand.html`，
而该文章的真实地址为http://me.tryblockchain.org/bitcoin-blockchain-misunderstand.html

因此需要进行拼接。

如果不需要拼接，`splice_base_url`字段可为空。

#### 样例
```ini
[me_tryblockchain_org]
mode=pagination
page_name=me_tryblockchain_org
page_url=http://me.tryblockchain.org{0}
page_pagination_url=/all_{0}.html
start_pagination_number=2
page_is_end=404
article_xpath=//*[@id="main-content"]/div[1]/div[1]/div/div[{0}]
article_url_xpath=/a/@href
start_article_number=1
end_article_number=20
article_number_gap=1
title_xpath=//*[@id="main-content"]/div[1]/div[1]/div/div[1]/h1/text()
content_xpath=//*[@id="main-content"]/div[1]/div[1]/div/div[2]
detail_splice_flag=true
splice_base_url=http://me.tryblockchain.org/{0}
```
注意`page_url`和`page_pagination_url`字段中的`{0}`，这是python进行字符串格式化所必须的写法，如上述样例中，该网站第二页的真实url为http://me.tryblockchain.org/all_2.html

详情请查看python的`format()`函数，`splice_base_url`字段中的`{0}`同理。

对于网站中一个页面的所有文章，一般而言它们的xpath路径都是有规律的，只是最后的编号不同，`article_xpath`字段中的`{0}`代表文章在网页HTML代码中的标签的顺序编号。

例如在上述样例中，一页有20篇文章，`//*[@id="main-content"]/div[1]/div[1]/div/div[1]`表示第一篇文章在HTML代码中的标签的位置，`//*[@id="main-content"]/div[1]/div[1]/div/div[20]`表示最后一篇文章在HTML代码中的标签的位置（如不理解请自学一下xpath的相关知识），因此文章编号的起始是1，结束是20，间隔是1，体现在配置文件中如下所示：
```ini
article_xpath=//*[@id="main-content"]/div[1]/div[1]/div/div[{0}]
article_url_xpath=/a/@href
start_article_number=1
end_article_number=20
article_number_gap=1
```
`article_xpath`字段中的`{0}`在爬取时将使用文章编号进行替换，以达到遍历所有文章的目的。

`article_url_xpath`为文章url在HTML代码中的标签的xpath路径，一般而言它是在文章xpath路径指代的HTML标签内部，因此只需填写拼接部分即可，例如上述样例中，文章url的真实xpath路径为`//*[@id="main-content"]/div[1]/div[1]/div/div[{0}]/a/@href`。
同理，`{0}`在爬取时将使用文章编号进行替换，以达到遍历的目的。

`title_xpath`和`content_xpath`分别代表爬取文章详情时，文章标题和内容的xpath路径，根据HTML代码结构填写即可。

### 动态加载页面的网站
#### 说明
```ini
[网页名称]
mode=dynamic loading
page_name=网页名称
page_url=网页url地址
request_method=网页请求方式（get|post）
request_param=网页请求参数
page_is_end=判断网页分页是否结束的方法（404|single page|xpath路径）
article_xpath=文章在HTML代码中的标签的xpath路径
article_url_xpath=文章url在HTML代码中的标签的xpath路径
start_article_number=文章在HTML代码中的标签的开始编号
end_article_number=文章在HTML代码中的标签的结束编号
article_number_gap=编号间隔
title_xpath=文章标题的xpath路径
content_xpath=文章内容的xpath路径
detail_splice_flag=爬取文章详情时，url是否需要拼接（true|false）
splice_base_url=拼接的基础url
```
`request_method`字段有两个选项：
1. get（表示网页请求方式为get）
2. post（表示网页请求方式为post）

`request_param`字段表示网页请求时的参数，写法按python字典形式，详见下面的样例。

配置其余字段同上文所述。

#### 样例
```ini
[oschina_net_u_3782027]
mode=dynamic loading
page_name=oschina_net_u_3782027
page_url=https://my.oschina.net/u/3782027
request_method=get
request_param={{'catalogId': 0, 'q': '', 'p': {0}, 'type': 'ajax'}}
page_is_end=//*[@id="newestBlogList"]/div[1]/div[1]
article_xpath=//*[@id="newestBlogList"]/div[1]/div[{0}]
article_url_xpath=/div[1]/a/@href
start_article_number=1
end_article_number=20
article_number_gap=1
title_xpath=//*[@id="mainScreen"]/div/div[1]/div/div[2]/div[1]/div[2]/h1/text()
content_xpath=//*[@id="articleContent"]
detail_splice_flag=false
splice_base_url=
```
注意`request_param`字段，必须将字典首尾的花括号加倍，否则`format()`函数格式化字符串时会有问题。

请求参数字典中的`p`字段代表翻页参数，因此也需要使用`{0}`填写以便爬虫进行遍历。请求参数字典的配置因网站而异，需要具体网页具体分析。
