
# Spring Boot Profile Service with Neo4J

This project provides cerate and read actions for profile service using Neo4J as databse 

## Features
- **Create Operations**: Create new user profile
- **Read Operations**: Read specific user profile using userId

## Setup
Intialize Spring boot project with Spring Web, Lombok, Spring Data Neo4j and add ModelMapper

### 1. Update pom.xml of Authentication Service

Create CharacterProfile class in entity packages

```java
  <properties>
	.....
 	<spring-cloud.version>2023.0.2</spring-cloud.version>   <!-- find the matching version for spring cloud with sprint boot on google -->
 </properties>
 <dependencies>
  .....
    <dependency>
	<groupId>org.springframework.cloud</groupId>
	<artifactId>spring-cloud-starter-openfeign</artifactId>
	<version>4.1.3</version>
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


```

Modify AuthServiceApplication

```.java
@SpringBootApplication
@EnableFeignClients
public class AuthServiceApplication {
	@Bean
	public ModelMapper modelMapper(){
		ModelMapper modelMapper = new ModelMapper();
		modelMapper.getConfiguration().setFieldMatchingEnabled(true);
		return modelMapper;
	}

	@Bean
	PasswordEncoder passwordEncoder(){
		return new BCryptPasswordEncoder(5);
	}
	public static void main(String[] args) {
		SpringApplication.run(AuthServiceApplication.class, args);
	}

}

```

Create ProfileClient inside httpClient package of repository

```.java
@FeignClient(name = "profile-service", url = "${app.service.profile}")
public interface ProfileClient {
    @PostMapping(value="/internal", produces = MediaType.APPLICATION_JSON_VALUE)
    CharacterProfileResponse createProfile(@RequestBody ProfileCreationRequest request);
}


```

Modify UserService class

```.java
    ....
    ProfileClient profileClient;


    public UserResponse createUser(UserCreationRequest request){
        if(userRepository.existsByUsername(request.getUsername())){
            throw new AppException(ErrorCode.USER_EXISTED);
        }
        User createdUser = modelMapper.map(request, User.class);
        createdUser.setPassword(passwordEncoder.encode(request.getPassword()));
        var roles = roleRepository.findAllById(request.getRoles());
        createdUser.setRoles(new HashSet<>(roles));
        userRepository.save(createdUser);

        ProfileCreationRequest profileCreationRequest = modelMapper.map(request, ProfileCreationRequest.class);
        profileCreationRequest.setUserId(createdUser.getId());
        profileClient.createProfile(profileCreationRequest);
        return modelMapper.map(createdUser, UserResponse.class);
    }
    ....
```

### 2. Update pom.xml of Character Profile Service

```pom.xml
		<!-- https://mvnrepository.com/artifact/org.springframework.boot/spring-boot-starter-oauth2-resource-server -->
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
			<version>3.3.2</version>
		</dependency>
		<!-- https://mvnrepository.com/artifact/com.nimbusds/nimbus-jose-jwt -->
		<dependency>
			<groupId>com.nimbusds</groupId>
			<artifactId>nimbus-jose-jwt</artifactId>
			<version>9.40</version>
		</dependency>
```

Add ApiResponse in dto.response package

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

### 3. Add exception package


Add AppException class

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

Add ErrorCode

```
@Getter
public enum ErrorCode {
    UNCATEGORIZED_EXCEPTION(500, "Uncategorized error", HttpStatus.INTERNAL_SERVER_ERROR), //INTERNAL_SERVER_ERROR => code = 500
    INVALID_KEY(400, "Uncategorized error", HttpStatus.BAD_REQUEST),
    USER_EXISTED(400, "User existed",HttpStatus.BAD_REQUEST),
    USER_NOT_EXISTED(404, "User not existed", HttpStatus.NOT_FOUND),
    UNAUTHENTICATED(401, "User is not authenticated", HttpStatus.UNAUTHORIZED), //UNAUTHORIZED => code = 401
    UNAUTHORIZED(403, "You do not have permission", HttpStatus.FORBIDDEN);
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

Add GlobalExceptionHandler

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

### 4. Add config package

Add CustomJwtDecoder

```
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

Add JwtAuthenticationEntryPoint

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

Add SecurityConfig

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
