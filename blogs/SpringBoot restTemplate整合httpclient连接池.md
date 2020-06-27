# [SpringBoot
restTemplate整合httpclient连接池](https://blog.csdn.net/hellozpc/article/details/106861972)

**欢迎关注公众号**

![](https://img-blog.csdnimg.cn/20191121223121694.jpg)

**微信扫一扫**

使用http连接池能够减少连接建立与释放的时间，提升http请求的性能。如果客户端每次请求都要和服务端建立新的连接，即三次握手将会非常耗时。本文介绍如何在Springboot中集成http连接池；基于restTemplate+httpclient实现。

### 文章目录

* 引入apache httpclient
* RestTemplate配置类
* RestTemplate连接池配置参数
* 测试带连接池的RestTemplate
* 注意事项

## 引入apache httpclient



    <dependency>
        <groupId>org.apache.httpcomponents</groupId>
        <artifactId>httpclient</artifactId>
        <version>4.5.6</version>
    </dependency>

## RestTemplate配置类

    import org.apache.http.client.HttpClient;
    import org.apache.http.impl.client.HttpClientBuilder;
    import org.springframework.boot.context.properties.ConfigurationProperties;
    import org.springframework.context.annotation.Bean;
    import org.springframework.context.annotation.Configuration;
    import org.springframework.http.client.ClientHttpRequestFactory;
    import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
    import org.springframework.http.client.SimpleClientHttpRequestFactory;
    import org.springframework.http.converter.HttpMessageConverter;
    import org.springframework.http.converter.StringHttpMessageConverter;
    import org.springframework.web.client.RestTemplate;
    
    import java.nio.charset.Charset;
    import java.util.List;
    import java.util.concurrent.TimeUnit;
    
    /**
     * 实际开发中要避免每次http请求都实例化httpclient
     * restTemplate默认会复用连接,保证restTemplate单例即可
     * 参考资料：
     * https://www.cnblogs.com/xrq730/p/10963689.html
     * https://halfrost.com/advance_tcp/
     */
    
    @Configuration
    public class RestTemplateConfig {
    
        @Bean
        RestTemplate restTemplate(ClientHttpRequestFactory clientHttpRequestFactory) {
            RestTemplate restTemplate = new RestTemplate(clientHttpRequestFactory);
            List<HttpMessageConverter<?>> messageConverters = restTemplate.getMessageConverters();
            for (HttpMessageConverter c : messageConverters) {
                if (c instanceof StringHttpMessageConverter) {
                    ((StringHttpMessageConverter) c).setDefaultCharset(Charset.forName("utf-8"));
                }
            }
    
            return restTemplate;
        }
    
        @Bean
        @ConfigurationProperties(prefix = "spring.resttemplate")
        HttpClientProperties httpClientProperties() {
            return new HttpClientProperties();
        }
    
        @Bean
        ClientHttpRequestFactory clientHttpRequestFactory(HttpClientProperties httpClientProperties) {
            //如果不使用HttpClient的连接池，则使用restTemplate默认的SimpleClientHttpRequestFactory,底层基于HttpURLConnection
            if (!httpClientProperties.isUseHttpClientPool()) {
                SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
                factory.setConnectTimeout(httpClientProperties.getConnectTimeout());
                factory.setReadTimeout(httpClientProperties.getReadTimeout());
                return factory;
            }
    
            //HttpClient4.3及以上版本不手动设置HttpClientConnectionManager,默认就会使用连接池PoolingHttpClientConnectionManager
            HttpClient httpClient = HttpClientBuilder.create().setMaxConnTotal(httpClientProperties.getMaxTotalConnect())
                    .setMaxConnPerRoute(httpClientProperties.getMaxConnectPerRoute()).evictExpiredConnections()
                    .evictIdleConnections(5000, TimeUnit.MILLISECONDS).build();
            HttpComponentsClientHttpRequestFactory factory = new HttpComponentsClientHttpRequestFactory(httpClient);
            factory.setConnectTimeout(httpClientProperties.getConnectTimeout());
            factory.setReadTimeout(httpClientProperties.getReadTimeout());
            factory.setConnectionRequestTimeout(httpClientProperties.getConnectionRequestTimeout());
            return factory;
        }
    
    }

## RestTemplate连接池配置参数

    ​```
    public class HttpClientProperties {
    
        /**
         * 是否使用httpclient连接池
         */
        private boolean useHttpClientPool = false;
    
        /**
         * 从连接池中获得一个connection的超时时间
         */
        private int connectionRequestTimeout = 3000;
    
        /**
         * 建立连接超时时间
         */
        private int connectTimeout = 3000;
    
        /**
         * 建立连接后读取返回数据的超时时间
         */
        private int readTimeout = 5000;
    
        /**
         * 连接池的最大连接数，0代表不限
         */
        private int maxTotalConnect = 128;
    
        /**
         * 每个路由的最大连接数
         */
        private int maxConnectPerRoute = 32;
    
        public int getConnectionRequestTimeout() {
            return connectionRequestTimeout;
        }
    
        public void setConnectionRequestTimeout(int connectionRequestTimeout) {
            this.connectionRequestTimeout = connectionRequestTimeout;
        }
    
        public int getConnectTimeout() {
            return connectTimeout;
        }
    
        public void setConnectTimeout(int connectTimeout) {
            this.connectTimeout = connectTimeout;
        }
    
        public int getReadTimeout() {
            return readTimeout;
        }
    
        public void setReadTimeout(int readTimeout) {
            this.readTimeout = readTimeout;
        }
    
        public int getMaxTotalConnect() {
            return maxTotalConnect;
        }
    
        public void setMaxTotalConnect(int maxTotalConnect) {
            this.maxTotalConnect = maxTotalConnect;
        }
    
        public int getMaxConnectPerRoute() {
            return maxConnectPerRoute;
        }
    
        public void setMaxConnectPerRoute(int maxConnectPerRoute) {
            this.maxConnectPerRoute = maxConnectPerRoute;
        }
    
        public boolean isUseHttpClientPool() {
            return useHttpClientPool;
        }
    
        public void setUseHttpClientPool(boolean useHttpClientPool) {
            this.useHttpClientPool = useHttpClientPool;
        }
    }
    
    ​```

application.properties

    ​```
    spring.resttemplate.connectionRequestTimeout=3000
    spring.resttemplate.connectTimeout=3000
    spring.resttemplate.readTimeout=10000
    spring.resttemplate.maxTotalConnect=256
    spring.resttemplate.maxConnectPerRoute=128
    spring.resttemplate.useHttpClientPool=true
    
    ​```

## 测试带连接池的RestTemplate

    ​```
    import com.alibaba.fastjson.JSON;
    import org.junit.Test;
    import org.junit.runner.RunWith;
    import org.springframework.beans.factory.annotation.Autowired;
    import org.springframework.boot.test.context.SpringBootTest;
    import org.springframework.http.HttpEntity;
    import org.springframework.http.HttpHeaders;
    import org.springframework.http.HttpMethod;
    import org.springframework.http.ResponseEntity;
    import org.springframework.test.context.junit4.SpringRunner;
    import org.springframework.web.client.RestTemplate;
    import org.springframework.web.util.UriComponentsBuilder;
    import java.util.Arrays;
    import java.util.List;
    import java.util.concurrent.ThreadLocalRandom;
    
    @RunWith(SpringRunner.class)
    @SpringBootTest
    public class RestTemplateTest {
    
        /**
         * 免费查询号码归属地接口
         */
        public String testUrl = "https://tcc.taobao.com/cc/json/mobile_tel_segment.htm";
    
        @Autowired
        RestTemplate restTemplate;
    
        @Test
        public void testRest() {
            HttpHeaders headers = new HttpHeaders();
            headers.set("Accept", "application/json");
            HttpEntity entity = new HttpEntity(headers);
    
            long start = System.currentTimeMillis();
            for (int i = 0; i < 1000; i++) {
                String tel = getRandomTel();
                UriComponentsBuilder builder = UriComponentsBuilder.fromHttpUrl(testUrl).queryParam("tel", tel);
                System.out.println("发送请求：" + builder.build().encode().toUri());
                long startInner = System.currentTimeMillis();
                ResponseEntity<String> getDistrictRes = restTemplate.exchange(builder.build().encode().toUri(), HttpMethod.GET, entity, String.class);
                long endInner = System.currentTimeMillis();
                System.out.print("costPerRequest:" + (endInner - startInner) + ",i=" + i + "," + Thread.currentThread().getName());
                String resJson = getDistrictRes.getBody().split("=")[1];
                String carrier = (String) JSON.parseObject(resJson).get("carrier");
                System.out.println("," + tel + ",归属地:" + carrier);
            }
    
            long end = System.currentTimeMillis();
            System.out.println("costTotal:" + (end - start));
        }
    
        private String getRandomTel() {
            List<String> telList = Arrays.asList("18120168516", "15952044278", "15537788259", "18751872329", "13913329187");
            int index = ThreadLocalRandom.current().nextInt(telList.size());
            return telList.get(index);
        }
    
    }
    
    ​```

测试比较发现，如果不设置ClientHttpRequestFactory，resttemplate默认会使用SimpleClientHttpRequestFactory，底层基于HttpURLConnection；这种方式和手动设置带连接池的httpComponentsClientHttpRequestFactory性能差别不大，基于httpclient的连接池性能稍有优势，不是太明显。

不管是使用restTemplate默认的SimpleClientHttpRequestFactory还是使用httpclient提供的HttpComponentsClientHttpRequestFactory，都会进行连接复用，即只有第一次请求耗时较高，后面的请求都复用连接。

使用httpclient可以设置evictExpiredConnections、evictIdleConnections进行定时清理过期、闲置连接。底层是开启了一个线程去执行清理任务，因此注意不能多次实例化httpclient相关的实例，会导致不断创建线程。

## 注意事项

  * 实际开发中要避免每次http请求都实例化httpclient
  * restTemplate默认会复用连接,保证restTemplate单例即可
  * 参考资料：
https://www.cnblogs.com/xrq730/p/10963689.html
https://halfrost.com/advance_tcp/

