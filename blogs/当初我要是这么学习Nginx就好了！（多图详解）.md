# [当初我要是这么学习Nginx就好了！（多图详解）](https://www.jianshu.com/p/215600b11413)

> 以下文章来源于51CTO技术栈 ，作者李航

本文主要帮助大家熟悉 Nginx 有哪些应用场景、Nginx 特点和架构模型以及相关流程、Nginx 定制化开发的几种模块分类。读完本文你将对 Nginx
有一定的认识。

#### 本文将围绕如下几个部分进行讲解：

  * **Nginx 简介及特点**

  * **Nginx 应用场景**

  * **Nginx 框架模型介绍**

  * **Nginx 内部流程介绍**

  * **Nginx 自定义模块开发介绍**

  * **Nginx 核心时间点模块介绍**

  * **Nginx 分流模块介绍**

  * **Nginx 动态 upstream 模块介绍**

  * **Nginx query_upstrem 模块介绍**

  * **Nginx query_conf 模块介绍**

  * **Nginx 共享内存支持 Redis 协议模块介绍**

  * **Nginx 日志回放压测工具介绍**

Nginx 简介以及特点

Nginx (engine x) 是一个高性能的 Web 服务器和反向代理服务器，也是一个 IMAP/POP3/SMTP 服务器：

  * 它由俄罗斯程序员 Igor Sysoev 于 2002 年开始开发。

  * Nginx 是增长最快的 Web 服务器，市场份额已达 33.3％。

  * 全球使用量排名第二，2011 年成立商业公司。

Nginx 社区分支：

  * **Openresty：** 作者 @agentzh（章宜春）开发的，最大特点是引入了 ngx_lua 模块，支持使用 Lua 开发插件，并且集合了很多丰富的模块，以及 Lua 库。

  * **Tengine：** 主要是淘宝团队开发。特点是融入了因淘宝自身的一些业务带来的新功能。

  * **Nginx 官方版本，** 更新迭代比较快，并且提供免费版本和商业版本。

Nginx 源码结构（代码量大约 11 万行 C 代码）：

  * **源代码目录结构 Core（主干和基础设置）**

  * **Event（事件驱动模型和不同的 IO 复用模块）**

  * **HTTP（HTTP 服务器和模块）**

  * **Mail（邮件代理服务器和模块）**

  * **OS（操作系统相关的实现）**

  * **Misc（杂项）**

Nginx 特点如下：

  * **反向代理，负载均衡器**

  * **高可靠性、单 Master 多 Worker 模式**

  * **高可扩展性、高度模块化**

  * **非阻塞**

  * **事件驱动**

  * **低内存消耗**

  * **热部署**

Nginx 应用场景

Nginx 的应用场景如下：

  * **静态文件服务器**

  * **反向代理，负载均衡**

  * **安全防御**

  * **智能路由（企业级灰度测试、地图 POI 一键切流）**

  * **灰度发布**

  * **静态化**

  * **消息推送**

  * **图片实时压缩**

  * **防盗链**

Nginx 框架模型介绍

进程组件角色：

  * **Master 进程：** 监视工作进程的状态；当工作进程死掉后重启一个新的；处理信号和通知工作进程。

  * **Worker 进程：** 处理客户端请求，从主进程处获得信号做相应的事情。

  * **Cache Loader 进程：** 加载缓存索引文件信息，然后退出。

  * **Cache Manager进程：** 管理磁盘的缓存大小，超过预定值大小后最少使用数据将被删除。

Nginx 的框架模型如下图：

![](https://upload-images.jianshu.io/upload_images/19895418-effd732e731dc3fa)

框架模型流程如下图：

![](https://upload-images.jianshu.io/upload_images/19895418-fc415162935ec09f)

Nginx 内部流程介绍

## Nginx 框架模型流程如下图：

![](https://upload-images.jianshu.io/upload_images/19895418-89b419f2c4bfc278)

![](https://upload-images.jianshu.io/upload_images/19895418-caf753a5cd59053f)

## Master 初始化流程，如下图：

![](https://upload-images.jianshu.io/upload_images/19895418-fc7598cc13561c8a)

## Worker 初始化：

![](https://upload-images.jianshu.io/upload_images/19895418-014ed8c53543cd12)

## Worker 初始化流程图如下：

![](https://upload-images.jianshu.io/upload_images/19895418-fc6c7c5f8358acf6)

## 静态文件请求 IO 流程如下图：

![](https://upload-images.jianshu.io/upload_images/19895418-35549181872219af)

## HTTP 请求流程如下图：

![](https://upload-images.jianshu.io/upload_images/19895418-81835fb38b8ecb78)

## HTTP 请求 11 个阶段，如下图所示：

![](https://upload-images.jianshu.io/upload_images/19895418-24d9e0aecd81dc77)

## upstream模块：

  * **访问第三方 Server 服务器**

  * **底层 HTTP 通信非常完善**

  * **异步非阻塞**

  * **上下游内存零拷贝，节省内存**

  * **支持自定义模块开发**

### upstream 框架流程，如下图：

![](https://upload-images.jianshu.io/upload_images/19895418-ffa0c250795fc4ed)

### upstream 内部流程，如下图：

![](https://upload-images.jianshu.io/upload_images/19895418-04312cae4612c8c2)

## 反向代理流程，如下图：

![](https://upload-images.jianshu.io/upload_images/19895418-c6c214331954d009)

Nginx 定制化模块开发

## Nginx 的模块化设计特点如下：

  * 高度抽象的模块接口

  * 模块接口非常简单，具有很高的灵活性

  * 配置模块的设计

  * 核心模块接口的简单化

  * 多层次、多类别的模块设计

## 内部核心模块：

![](https://upload-images.jianshu.io/upload_images/19895418-69adf13b6d5e732d)

![](https://upload-images.jianshu.io/upload_images/19895418-327302eb2b2bef11)

##  **Handler 模块：** 接受来自客户端的请求并构建响应头和响应体。

![](https://upload-images.jianshu.io/upload_images/19895418-ae77fe6ffd7325f8)

##  **Filter 模块：**
过滤（filter）模块是过滤响应头和内容的模块，可以对回复的头和内容进行处理。它的处理时间在获取回复内容之后，向用户发送响应之前。

![](https://upload-images.jianshu.io/upload_images/19895418-cdb9b46334e537a8)

##  **Upstream 模块：** 使 Nginx 跨越单机的限制，完成网络数据的接收、处理和转发，纯异步的访问后端服务。

![](https://upload-images.jianshu.io/upload_images/19895418-a29207c324baa088)

**Load_Balance：** 负载均衡模块，实现特定的算法，在众多的后端服务器中，选择一个服务器出来作为某个请求的转发服务器。

![](https://upload-images.jianshu.io/upload_images/19895418-cf205cfaba56bd4c)

## ngx_lua 模块：

  * **脚本语言**

  * **内存开销小**

  * **运行速度快**

  * **强大的 Lua 协程**

  * **非阻塞**

  * **业务逻辑以自然逻辑书写**

![](https://upload-images.jianshu.io/upload_images/19895418-391172812c5c7be4)

## **定制化开发 Demo**

Handler 模块：

  * **编写 config 文件**

  * **编写模块产生内容响应信息**

    ```
    #配置文件：
    server {
        ...
        location test {
            test_counter on;
        }
    }
    #config
    ngx_addon_name=ngx_http_test_module
    HTTP_MODULES="$HTTP_MODULES ngx_http_test_module"
    NGX_ADDON_SRCS="$NGX_ADDON_SRCS $ngx_addon_dir/ngx_http_test_module.c"
    #ngx_http_test_module.c
    static ngx_int_t
    ngx_http_test_handler(ngx_http_request_t *r)
    {
        ngx_int_t                               rc;
        ngx_buf_t                               *b;
        ngx_chain_t                             out;
        ngx_http_test_conf_t                    *lrcf;
        ngx_str_t                               ngx_test_string = ngx_string("hello test");

        lrcf = ngx_http_get_module_loc_conf(r, ngx_http_test_module);
        if ( lrcf->test_counter == 0 ) {
            return NGX_DECLINED;
        }

        /* we response to 'GET' and 'HEAD' requests only */
        if ( !(r->method & (NGX_HTTP_GET|NGX_HTTP_HEAD)) ) {
                return NGX_HTTP_NOT_ALLOWED;
        }

        /* discard request body, since we don't need it here */
        rc = ngx_http_discard_request_body(r);

        if ( rc != NGX_OK ) {
            return rc;
        }

        /* set the 'Content-type' header */
        /*
         *r->headers_out.content_type.len = sizeof("text/html") - 1;
         *r->headers_out.content_type.data = (u_char *)"text/html";
        */
        ngx_str_set(&r->headers_out.content_type, "text/html");

        /* send the header only, if the request type is http 'HEAD' */
        if ( r->method == NGX_HTTP_HEAD ) {
            r->headers_out.status = NGX_HTTP_OK;
            r->headers_out.content_length_n = ngx_test_string.len;

            return ngx_http_send_header(r);
        }

        /* set the status line */
        r->headers_out.status = NGX_HTTP_OK;
        r->headers_out.content_length_n =  ngx_test_string.len;

        /* send the headers of your response */
        rc = ngx_http_send_header(r);
        if ( rc == NGX_ERROR || rc > NGX_OK || r->header_only ) {
            return rc;
        }

        /* allocate a buffer for your response body */
        b = ngx_pcalloc(r->pool, sizeof(ngx_buf_t));
        if ( b == NULL ) {
            return NGX_HTTP_INTERNAL_SERVER_ERROR;
        }

        /* attach this buffer to the buffer chain */
        out.buf = b;
        out.next = NULL;

        /* adjust the pointers of the buffer */
        b->pos = ngx_test_string.data;
        b->last = ngx_test_string.data + ngx_test_string.len;
        b->memory = 1;    /* this buffer is in memory */
        b->last_buf = 1;  /* this is the last buffer in the buffer chain */

        /* send the buffer chain of your response */
        return ngx_http_output_filter(r, &out);
    }
    ```

Nginx 核心时间点模块介绍

解决接入层故障定位慢的问题，帮助 OP 快速判定问题根因，优先自证清白，提高接入层高效的生产力。

![](https://upload-images.jianshu.io/upload_images/19895418-c0dc4d6e7236cd71)

Nginx 分流模块介绍

Nginx 分流模块特点如下：

  * **实现非常灵活的动态的修改策略从而进行切流量。**

  * **实现平滑无损的方式进行流量的切换。**

  * **通过秒级切换流量可以缩小影响范围，从而减少损失。**

  * **按照某一城市或者某个特征，秒级进行切换流量或者禁用流量。**

  * **容忍单机房级别容量故障，缩短了单机房故障的止损时间。**

  * **快速的将流量隔离或者流量抽样。**

  * **高效的灰度测试，提高生产力。**

![](https://upload-images.jianshu.io/upload_images/19895418-5800583538bf9e4a)

Nginx 动态 upstream 模块介绍

让接入层可以适配动态调度的云环境，实现服务的平滑上下线、弹性扩/缩容。

从而提高接入层高效的生产力以及稳定性，保证业务流量的平滑无损。

![](https://upload-images.jianshu.io/upload_images/19895418-e2c1cbf9726f035d)

Nginx query_upstream 模块介绍

链路追踪，梳理接口到后端链路的情况。查询 location 接口对应 upstream server 信息。

![](https://upload-images.jianshu.io/upload_images/19895418-6ef1f5b7ab9bd61d)

Nginx query_conf 模块介绍

获取 Nginx 配置文件格式化为 json 格式信息：

![](https://upload-images.jianshu.io/upload_images/19895418-7adb3506d5c077a4)

Nginx 共享内存支持 Redis 协议模块介绍

根据配置文件来动态的添加共享内存：

    ```
    https://github.com/lidaohang/ngx_shm_dict
    ```

**ngx_shm_dict：** 共享内存核心模块（红黑树，队列） **ngx_shm_dict_manager：**
添加定时器事件，定时的清除共享内存中过期的 Key，添加读事件，支持 Redis 协议，通过 redis-cli get，set，del，ttl
**ngx_shm_dict_view：** 共享内存查看

![](https://upload-images.jianshu.io/upload_images/19895418-8718db8ffc7bd971)

Nginx 日志回放压测工具

解析日志进行回放压测，模拟后端服务器慢等各种异常情况 ：

    ```
    https://github.com/lidaohang/playback-testing
    ```

#### 方案说明：

  * 客户端解析 access.log 构建请求的 host，port，url，body。

  * 把后端响应时间，后端响应状态码，后端响应大小放入 header 头中。

  * 后端服务器获取相应的 header，进行模拟响应 body 大小，响应状态码，响应时间。

#### 使用方式：

  * 拷贝需要测试的 access.log 的日志到 logs 文件夹里面。

  * 搭建需要测试的 Nginx 服务器，并且配置 upstream 指向后端服务器断端口

  * 启动后端服务器实例

    ```
    server/backserver/main.go
    ```

  * 进行压测

    ```
    bin/wrk -c30 -t1 -s conf/nginx_log.lua http://localhost:8095
    ```

_作者：李航_

_简介：多年的底层开发经验，在高性能 Nginx 开发和分布式缓存 Redis Cluster 有着丰富的经验，目前从事分布式存储工作。先后在 58
同城、汽车之家、优酷土豆集团工作。目前供职于滴滴基础平台-技术专家岗位，主要负责分布式 Ceph 系统。个人主要关注的技术领域：高性能 Nginx
开发、分布式缓存、分布式存储。_

_编辑：陶家龙_

