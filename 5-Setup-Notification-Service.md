
# Spring Boot Profile Service with Neo4J

This project provides cerate and read actions for profile service using Neo4J as databse 

## Features
- **Create Operations**: Create new user profile
- **Read Operations**: Read specific user profile using userId

## Setup
Intialize Spring boot project with Spring Web, Lombok, Spring Data Neo4j and add ModelMapper

### 1. Install MongoDB on Docker

For Mac M1

```bash
docker pull mongodb/mongodb-community-server:6.0-ubi8
```

```bash
docker run --name mongodb -d -p 27017:27017 -e MONGODB_INITDB_ROOT_USERNAME=root -e MONGODB_INITDB_ROOT_PASSWORD=18091999Dat mongodb/mongodb-community-server:6.0-ubi8
```

### 2. Update pom.xml of Character Profile Service

```pom.xml
	<properties>
		<java.version>17</java.version>
		<spring-cloud.version>2023.0.2</spring-cloud.version>
	</properties>

	 <dependencies>
		.....
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
		</dependency>
		<!-- https://mvnrepository.com/artifact/org.springframework.cloud/spring-cloud-starter-openfeign -->
		<dependency>
			<groupId>org.springframework.cloud</groupId>
			<artifactId>spring-cloud-starter-openfeign</artifactId>
			<version>4.1.3</version>
		</dependency>
		.....
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
```

### 3. Config MongoDB in SpringBoot, and default code

In application.properties set MongoDB config

```
spring.application.name=notification-service
server.port:8082
# MongoDB Configuration
spring.data.mongodb.uri:mongodb://root:18091999Dat@localhost:27017/notification-service?authSource=admin
```


# Add config package

CustomJwtDecoder,java
```java
@Component
@FieldDefaults(level = AccessLevel.PRIVATE)
public class CustomJwtDecoder implements JwtDecoder {

    @Override
    public Jwt decode(String token) throws JwtException {
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

JwtAuthenticationEntryPoint.java
```
public class JwtAuthenticationEntryPoint implements AuthenticationEntryPoint {

    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response, AuthenticationException authException) throws IOException, ServletException {
        ErrorCode errorCode = ErrorCode.UNAUTHENTICATED;
        response.setStatus(errorCode.getStatus().value());
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        ApiResponse<?> apiResponse = ApiResponse.builder().code(errorCode.getCode()).message(errorCode.getMessage()).build();
        ObjectMapper objectMapper = new ObjectMapper();
        response.getWriter().write(objectMapper.writeValueAsString(apiResponse));
        response.flushBuffer();
    }
}

```

SecurityConfig.java
```
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@FieldDefaults(level = AccessLevel.PRIVATE)
public class SecurityConfig {
    final String PUBLIC_ENDPOINTS[] = {"/profile-service/internal"};
    @Autowired
    CustomJwtDecoder customJwtDecoder;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity httpSecurity) throws Exception{
        httpSecurity.authorizeHttpRequests(
                request -> request.requestMatchers(HttpMethod.POST, PUBLIC_ENDPOINTS).permitAll()
                        .anyRequest().authenticated());

        httpSecurity.oauth2ResourceServer(oauth2 ->{
           oauth2.jwt(jwtConfigurer -> jwtConfigurer.decoder(customJwtDecoder).jwtAuthenticationConverter(jwtAuthenticationConverter()))
                   .authenticationEntryPoint(new JwtAuthenticationEntryPoint());
        });

        httpSecurity.csrf(httpSecurityCsrfConfigurer -> httpSecurityCsrfConfigurer.disable());
        return httpSecurity.build();
    }

    @Bean
    JwtAuthenticationConverter jwtAuthenticationConverter(){
        JwtGrantedAuthoritiesConverter jwtGrantedAuthoritiesConverter = new JwtGrantedAuthoritiesConverter();
        jwtGrantedAuthoritiesConverter.setAuthorityPrefix("");
        JwtAuthenticationConverter jwtAuthenticationConverter = new JwtAuthenticationConverter();
        jwtAuthenticationConverter.setJwtGrantedAuthoritiesConverter(jwtGrantedAuthoritiesConverter);
        return jwtAuthenticationConverter;

    }
}

```

# Add dto.response package

ApiResponse.java
```
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T> {
    int code = 200;
    String message;
    T result;
}
```

+ Add excepttion package

ErrorCode.java
```
public enum ErrorCode {
    UNCATEGORIZED_EXCEPTION(9999, "Uncategorized error", HttpStatus.INTERNAL_SERVER_ERROR),
    INVALID_KEY(1001, "Uncategorized error", HttpStatus.BAD_REQUEST),
    UNAUTHENTICATED(1006, "Unauthenticated", HttpStatus.UNAUTHORIZED),
    UNAUTHORIZED(1007, "You do not have permission", HttpStatus.FORBIDDEN),
    CANNOT_SEND_EMAIL(1008, "Cannot send email", HttpStatus.BAD_REQUEST);
    private int code;
    private String message;
    private HttpStatus status;
    ErrorCode(int code, String message, HttpStatus status){
        this.code = code;
        this.message = message;
        this.status = status;
    }
}

```

AppException,java
```
public class AppException extends RuntimeException{
    private ErrorCode errorCode;
    public AppException(ErrorCode errorCode){
        super(errorCode.getMessage());
        this.errorCode = errorCode;
    }

    public ErrorCode getErrorCode(){ return this.errorCode; }

    public void setErrorCode(ErrorCode errorCode){ this.errorCode = errorCode; }
}

```

GlobalExceptionHandler.java
```
@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(value = Exception.class)
    ResponseEntity<ApiResponse> handlingRuntimeException(RuntimeException exception){
        ApiResponse apiResponse = new ApiResponse<>();
        apiResponse.setCode(ErrorCode.UNCATEGORIZED_EXCEPTION.getCode());
        apiResponse.setMessage(ErrorCode.UNCATEGORIZED_EXCEPTION.getMessage());
        return ResponseEntity.badRequest().body(apiResponse);
    }

    @ExceptionHandler(value = AppException.class)
    ResponseEntity<ApiResponse> handlingAppException(AppException exception){
        ErrorCode errorCode = exception.getErrorCode();
        ApiResponse apiResponse = new ApiResponse();
        apiResponse.setCode(errorCode.getCode());
        apiResponse.setMessage(errorCode.getMessage());
        return ResponseEntity.status(errorCode.getStatus()).body(apiResponse);
    }

    @ExceptionHandler(value = AccessDeniedException.class)
    ResponseEntity<ApiResponse> handlingAccessDeniedException(AccessDeniedException exception){
        ErrorCode errorCode = ErrorCode.UNAUTHENTICATED;
        return ResponseEntity.status(errorCode.getStatus())
                .body(ApiResponse.builder().code(errorCode.getCode())
                        .message(errorCode.getMessage()).build());
    }
}

```

# Enable FeingCleint in application mian class

```
@SpringBootApplication
@EnableFeignClients
public class NotificationServiceApplication {
    .....
}
```

### 4. Add dto

# In Resquest package add the files below

Sender.java
```
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class Sender {
    String name;
    String email;
}
```

Recipient.java
```
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class Recipient {
    String name;
    String email;
}
```

EmailRequest.java
```
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class EmailRequest {
    Sender sender;
    List<Recipient> to;
    String subject;
    String htmlContent;
}
```

SendEmailRequest.java
```
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class SendEmailRequest {
    Recipient to;
    String subject;
    String htmlContent;
}
```

# In Response package add this file

EmailResponse.java
```
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class EmailResponse {
    String messageId;
}
```


# Create repository package and inside of that package create httpclient package and add this file

```
@FeignClient(name = "email-client", url = "https://api.brevo.com")
public interface EmailClient {
    @PostMapping(value = "/v3/smtp/email", produces = MediaType.APPLICATION_JSON_VALUE)
    EmailResponse sendEmail(@RequestHeader("api-key") String apiKey, @RequestBody EmailRequest body);
}
```

# Create service package and add this file

Register for an API token from Brevo

EmailService.java
```
@Service
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class EmailService {
    EmailClient emailClient;

    String apiKey = "get-your-api";

    public EmailResponse sendEmail(SendEmailRequest request) {
        EmailRequest emailRequest = EmailRequest.builder()
                .sender(Sender.builder()
                        .name("Animee")
                        .email("dlmochastore@gmail.com")
                        .build())
                .to(List.of(request.getTo()))
                .subject(request.getSubject())
                .htmlContent(request.getHtmlContent())
                .build();
        try {
            return emailClient.sendEmail(apiKey, emailRequest);
        } catch (FeignException e){
            throw new AppException(ErrorCode.CANNOT_SEND_EMAIL);
        }
    }
}

```


# Create controller package and add this file 

EmailController.java
```
@RestController
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class EmailController {
    EmailService emailService;

    @PostMapping("/email/send")
    ApiResponse<EmailResponse> sendEmail(@RequestBody SendEmailRequest request){
        return ApiResponse.<EmailResponse>builder()
                .result(emailService.sendEmail(request))
                .build();
    }
}

```

### 5. Add config for notification service in api-gateway/../applicaiton.properties

```
......


spring.cloud.gateway.routes[3].id=notification_service
spring.cloud.gateway.routes[3].uri=http://localhost:8082
spring.cloud.gateway.routes[3].predicates[0]=Path=${app.api-prefix}/notifications/**
spring.cloud.gateway.routes[3].filters[0]=StripPrefix=2

```
