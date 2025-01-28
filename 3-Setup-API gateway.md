
# Spring Boot Api Gatewway with Spring Cloud Gateway 

This project provides a setup api gateway by using Spring Cloud Starter Gateway

## Features

- **Request Routing**: routes incoming client requests to the appropriate microservice or backend service based on the request path, headers
- **Centralized Authentication and Authorization**: Ensures that all incoming requests are authenticated and authorized before reaching backend services.

### 1. Update dependency

Add these dependencies into pom.xml

```.xml
        
	<properties>
		.....
		<spring-cloud.version>2023.0.3</spring-cloud.version>
	</properties>
	<dependencies>
		......
        <dependency>
			<groupId>org.springframework.cloud</groupId>
			<artifactId>spring-cloud-starter-gateway</artifactId>
		</dependency>
		<dependency>
			<groupId>io.projectreactor</groupId>
			<artifactId>reactor-test</artifactId>
			<scope>test</scope>
		</dependency>
		<dependency>
			<groupId>io.netty</groupId>
			<artifactId>netty-resolver-dns-native-macos</artifactId>
			<version>4.1.114.Final</version> <!-- Match your current Netty version -->
			<classifier>osx-aarch_64</classifier> <!-- For ARM-based Macs (e.g., Apple Silicon) -->
		</dependency>
		<!-- https://mvnrepository.com/artifact/org.modelmapper/modelmapper -->
		<dependency>
			<groupId>org.modelmapper</groupId>
			<artifactId>modelmapper</artifactId>
			<version>3.1.1</version>
		</dependency>
	</dependencies>
	<dependencyManagement>
		<dependencies>
			<dependency>
				<groupId>org.springframework.cloud</groupId>
				<artifactId>spring-cloud-dependencies</artifactId>
				<version>${spring-cloud.version}</version>
				<type>pom</type>
				<scope>import</scope>
			</dependency>
		</dependencies>
	</dependencyManagement>

	<build>
		.....
	</build>

</project>

```

### 2. Setup application.properties and test

```java
spring.application.name=api-gateway
server.port=1234 
app.api-prefix=/api/v1
spring.cloud.gateway.routes[0].id=auth_service # Can be orther name doesn't need to match application name of Authentication Servic
spring.cloud.gateway.routes[0].uri=http://localhost:8080
spring.cloud.gateway.routes[0].predicates[0]=Path=${app.api-prefix}/auth-service/auth/**
spring.cloud.gateway.routes[0].filters[0]=StripPrefix=2

spring.cloud.gateway.routes[1].id=profile_service
spring.cloud.gateway.routes[1].uri=http://localhost:8081
spring.cloud.gateway.routes[1].predicates[0]=Path=${app.api-prefix}/profile-service/**
spring.cloud.gateway.routes[1].filters[0]=StripPrefix=2

spring.cloud.gateway.routes[2].id=users_service
spring.cloud.gateway.routes[2].uri=http://localhost:8080
spring.cloud.gateway.routes[2].predicates[0]=Path=${app.api-prefix}/auth-service/user/**
spring.cloud.gateway.routes[2].filters[0]=StripPrefix=2

```

### 3. Config security for gateway

Add IntrospectRequest to dto.request, IntrospectResponse, and ApiResponse in dto.response

```java
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class IntrospectRequest {
    String token;
}
```

```java
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class IntrospectResponse {
    boolean isValid;
}
```

```java
@AllArgsConstructor
@NoArgsConstructor
@Setter
@Getter
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {
    int code = 200;
    String message;
    T result;

    @Override
    public String toString(){
        return "{\n\tcode: " + code + "\n\tmessage: " + message + "\n\tresult: " + result + "\n}";
    }
}
```


Add into IdentityClient repository package

```java
import com.example.api_gateway.dto.request.IntrospectRequest;
import com.example.api_gateway.dto.response.ApiResponse;
import com.example.api_gateway.dto.response.IntrospectResponse;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.service.annotation.PostExchange;
import reactor.core.publisher.Mono;

public interface IdentityClient {
    @PostExchange(url = "/auth-service/introspect", contentType = MediaType.APPLICATION_JSON_VALUE)
    Mono<ApiResponse<IntrospectResponse>> introspect(@RequestBody IntrospectRequest request);
}
```

Add IdentityService into service package

```
import com.example.api_gateway.dto.request.IntrospectRequest;
import com.example.api_gateway.dto.response.ApiResponse;
import com.example.api_gateway.dto.response.IntrospectResponse;
import com.example.api_gateway.repository.IdentityClient;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Mono;

@Service
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class IdentityService {
    IdentityClient identityClient;

    public Mono<ApiResponse<IntrospectResponse>> introspect(String token){
        return identityClient.introspect(IntrospectRequest.builder().token(token).build());
    }
}

```

Add WebClientConfiguration and AuthenticationFilter into configuration package

WebClientConfiguration

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.support.WebClientAdapter;
import org.springframework.web.service.invoker.HttpServiceProxyFactory;

@Configuration
public class WebClientConfiguration {
    @Bean
    WebClient identityWebClient(){
        return WebClient.builder()
                .baseUrl("http://localhost:8080")
                .build();
    }

    @Bean
    IdentityClient identityClient(WebClient identityWebClient){
        HttpServiceProxyFactory httpServiceProxyFactory = HttpServiceProxyFactory.builderFor(WebClientAdapter.create(identityWebClient)).build();
        return httpServiceProxyFactory.createClient(IdentityClient.class);
    }
}

```

AuthenticationFilter

```java
import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.http.server.reactive.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.Arrays;
import java.util.List;

@Component
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PACKAGE, makeFinal = true)
@Slf4j
public class AuthenticationFilter implements GlobalFilter, Ordered {
    IdentityService identityService;
    ModelMapper modelMapper;
    @Value("${app.api-prefix}")
    @NonFinal
    private String apiPrefix;
    @NonFinal
    private String PUBLIC_ENDPOINTS[] = {"/auth-service/auth/.*", "/auth-service/user/registration"};

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        if(isPublicEndpoint(exchange.getRequest())) return chain.filter(exchange);

        List<String> authHeader = exchange.getRequest().getHeaders().get(HttpHeaders.AUTHORIZATION);
        if(CollectionUtils.isEmpty(authHeader)) return unauthenticated(exchange.getResponse());

        String token = authHeader.get(0).replace("Bearer", "");
        return identityService.introspect(token).flatMap(introspectResponseApiResponse -> {
           if(introspectResponseApiResponse.getResult().isValid()) return chain.filter(exchange);
           return unauthenticated(exchange.getResponse());
        }).onErrorResume(throwable ->
                unauthenticated(exchange.getResponse()));
    }

    @Override
    public int getOrder() {
        return 0;
    }

    Mono<Void> unauthenticated(ServerHttpResponse response){
        ApiResponse<?> apiResponse = ApiResponse.builder()
                .code(401)
                .message("Unauthenticated")
                .build();

        String body = apiResponse.toString();
        response.setStatusCode(HttpStatus.UNAUTHORIZED);
        response.getHeaders().add(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE);
        return response.writeWith(Mono.just(response.bufferFactory().wrap(body.getBytes())));
    }

    private boolean isPublicEndpoint(ServerHttpRequest request){
        return Arrays.stream(PUBLIC_ENDPOINTS).anyMatch(s -> request.getURI().getPath().matches(apiPrefix + s));
    }
}
```

### 4. Modify JwtDecoder in Authentication service to avoid duplicate authentication

Add AuthenticationRequestInterceptor into config package

```java
import feign.RequestInterceptor;
import feign.RequestTemplate;
import org.springframework.util.StringUtils;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

public class AuthenticationRequestInterceptor implements RequestInterceptor {

    @Override
    public void apply(RequestTemplate requestTemplate) {
        ServletRequestAttributes servletRequestAttributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        var authHeader = servletRequestAttributes.getRequest().getHeader("Authorization");
        if(StringUtils.hasText(authHeader)) requestTemplate.header("Authorization", authHeader);
    }
}
```

Modify CustomJwtDecoder in config package

```java
import com.nimbusds.jwt.SignedJWT;
import lombok.AccessLevel;
import lombok.experimental.FieldDefaults;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.JwtException;
import org.springframework.stereotype.Component;
import java.text.ParseException;

@Component
@FieldDefaults(level = AccessLevel.PRIVATE)
public class CustomJwtDecoder implements JwtDecoder {
    @Value("${jwt.signerKey}")
    String SIGNER_KEY;

    @Override
    public Jwt decode(String token) throws JwtException{
        try{
            SignedJWT signedJWT = SignedJWT.parse(token);
            return new Jwt(token,
                    signedJWT.getJWTClaimsSet().getIssueTime().toInstant(),
                    signedJWT.getJWTClaimsSet().getExpirationTime().toInstant(),
                    signedJWT.getHeader().toJSONObject(),
                    signedJWT.getJWTClaimsSet().getClaims());
        } catch (ParseException e){
            throw new JwtException("Invalid Exception");
        }
    }
}
```
