
# Spring Boot Banking Authentication API

This project provides a robust authentication and authorization system for a banking application, featuring JWT-based authentication, role-based access control (RBAC), and CRUD operations for users, roles, and permissions.

## Features

- **JWT-Based Authentication**: Issue JWT tokens and validate them for secure access via OAuth 2.0, allow to validate and refresh token if need.
- **Role-Based Access Control (RBAC)**: Manage roles and permissions for fine-grained access control using filter chain.
- **CRUD Operations**: Manage users, roles, and permissions.
- **Global Exception Handling**: Handles exceptions like `AccessDeniedException`, `AppException`, `MethodArgumentNotValidException`, and more.
- **Custom JWT Decoder**: A scalable JWT decoder that fits into Spring Security’s filter chain for JWT validation and authentication.

## Setup

### 1. Create simple CRUD actions for User Service

Create User class in entity packages

```java
@Entity
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    String id;
    String username;
    String password;
    String firstName;
    String lastName;
    LocalDate dob;
}

```

Create dto package with two sub packages request and response

In request package, creates UserCreationRequest class, and  UserUpdateRequest class


```java
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class UserCreationRequest {
    String username;
    String password;
    String firstName;
    String lastName;
    LocalDate dob;
}

```

```java
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class UserUpdateRequest {
    String password;
    String firstName;
    String lastName;
    LocalDate dob;
}

```

In response package, creates UserResponse class, and ApiResponse class

```java
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class UserResponse {
    String id;
    String username;
    String firstName;
    String lastName;
    LocalDate dob;
}

```

```java
@AllArgsConstructor
@NoArgsConstructor
@Setter
@Getter
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiResponse<T>{
    int code = 200;
    String message;
    T result;
}

```

Create the ErrorCode enum in enums package

```java
@FieldDefaults(level = AccessLevel.PRIVATE)
public enum ErrorCode {
    USER_EXISTED(400, "User existed", HttpStatus.BAD_REQUEST),
    USER_NOT_EXISTED(404, "User not existed", HttpStatus.NOT_FOUND);

    int code;
    String message;
    HttpStatus status;
    ErrorCode(int code, String message, HttpStatus status){
        this.code = code;
        this.message = message;
        this.status = status;
    }

}

```

Create AppException class in error package

```java
public class AppException extends RuntimeException{
    private ErrorCode errorCode;

    public AppException(ErrorCode errorCode){
        this.errorCode = errorCode;
    }

    public ErrorCode getErrorCode() {
        return errorCode;
    }

    public void setErrorCode(ErrorCode errorCode){
        this.errorCode = errorCode;
    }
}

```

Create UserRepository interface in repository package

```java
@Repository
public interface UserRepository extends JpaRepository<User, String> {
    boolean existsByUsername(String username);
    Optional<User> findByUsername(String username);
}

```

Register a bean of ModelMapper in the main class

```java
@SpringBootApplication
public class AuthServiceApplication {
	@Bean
	public ModelMapper modelMapper(){
		return new ModelMapper();
	}
	public static void main(String[] args) {
		SpringApplication.run(AuthServiceApplication.class, args);
	}

}
```

Create UserService class in service package

```java
@Service
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class UserService {
    UserRepository userRepository;
    ModelMapper modelMapper;


    public UserResponse createUser(UserCreationRequest request){
        if(userRepository.existsByUsername(request.getUsername())){
            throw new AppException(ErrorCode.USER_EXISTED);
        }
        User createdUser = modelMapper.map(request, User.class);
        userRepository.save(createdUser);
        return modelMapper.map(createdUser, UserResponse.class);
    }

    public UserResponse updateUser(String id, UserUpdateRequest request){
        User foundUser = userRepository.findById(id).orElseThrow(
                ()  -> new AppException(ErrorCode.USER_NOT_EXISTED)
        );
        foundUser.setPassword(request.getPassword());
        foundUser.setFirstName(request.getFirstName());
        foundUser.setLastName(request.getLastName());
        foundUser.setDob(request.getDob());
        userRepository.save(foundUser);
        return modelMapper.map(foundUser, UserResponse.class);
    }

    public void deleteUser(String id){
        User foundUser = userRepository.findById(id).orElseThrow(
                () -> new AppException(ErrorCode.USER_NOT_EXISTED)
        );
        userRepository.delete(foundUser);
    }

    public UserResponse getUserById(String id){
        User foundUser = userRepository.findById(id).orElseThrow(
                () -> new AppException(ErrorCode.USER_NOT_EXISTED)
        );
        return modelMapper.map(foundUser, UserResponse.class);
    }

    public List<UserResponse> getAllUser(){
        List<User> users = userRepository.findAll();
        return users.stream().map(user -> modelMapper.map(user, UserResponse.class)).toList();
    }
}

```

Create UserController in controller package

```java
@RestController
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
@RequestMapping("/auth-service/user")
public class UserController {
    UserService userService;

    @GetMapping
    public ApiResponse<List<UserResponse>> getAllUsers(){
        ApiResponse<List<UserResponse>> apiResponse = new ApiResponse<>();
        apiResponse.setResult(userService.getAllUser());
        return apiResponse;
    }

    @GetMapping("{id}")
    public ApiResponse<UserResponse> getUserById(@PathVariable String id){
        ApiResponse<UserResponse> apiResponse = new ApiResponse<>();
        apiResponse.setResult(userService.getUserById(id));
        return apiResponse;
    }

    @PostMapping
    public ApiResponse<UserResponse> createUser(@RequestBody UserCreationRequest request){
        ApiResponse<UserResponse> apiResponse = new ApiResponse<>();
        apiResponse.setResult(userService.createUser(request));
        return apiResponse;
    }

    @PostMapping("{id}")
    public ApiResponse<UserResponse> updateUser(@PathVariable String id, @RequestBody UserUpdateRequest request){
        ApiResponse<UserResponse> apiResponse = new ApiResponse<>();
        apiResponse.setResult(userService.updateUser(id, request));
        return apiResponse;
    }

    @DeleteMapping("{id}")
    public ApiResponse deleteUser(@PathVariable String id){
        try{
            userService.deleteUser(id);
        }catch (Exception e){
            return ApiResponse.builder().code(404).message("User is not existed!").result(ErrorCode.USER_NOT_EXISTED).build();
        }
        return ApiResponse.builder().code(200).message("Successfully deleted!").build();
    }
}

```
////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  //////// ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////

### 2. Create Authentication Service with generate token function allow us to create and sign our token

Add the jwt attributes to application.properties

```application.properties
jwt.signerKey=9pxzswn0GXIoxAAh3nIUIlhRAe98eFKJkSuOz0mXiTiZzad4PJTdXujLCVyE+kNM
jwt.valid-duration=3600
jwt.refreshable-duration=36000
```

Update dependencies inside pom.xml

```pom.xml
		<!-- https://mvnrepository.com/artifact/org.springframework.security/spring-security-crypto -->
		<dependency>
			<groupId>org.springframework.security</groupId>
			<artifactId>spring-security-crypto</artifactId>
		</dependency>
		<!-- https://mvnrepository.com/artifact/com.nimbusds/nimbus-jose-jwt -->
		<dependency>
			<groupId>com.nimbusds</groupId>
			<artifactId>nimbus-jose-jwt</artifactId>
			<version>9.40</version>
		</dependency>

```

Register a bean of ModelMapper in the main class

```java
@SpringBootApplication
public class AuthServiceApplication {
	........

	@Bean
	PasswordEncoder passwordEncoder(){
		return new BCryptPasswordEncoder(5);
	}
	public static void main(String[] args) {
		SpringApplication.run(AuthServiceApplication.class, args);
	}
}

```

Modify the createUser() method in UserService class to encode the user password

```java
    public UserResponse createUser(UserCreationRequest request){
        if(userRepository.existsByUsername(request.getUsername())){
            throw new AppException(ErrorCode.USER_EXISTED);
        }
        User createdUser = modelMapper.map(request, User.class);
        createdUser.setPassword(passwordEncoder.encode(request.getPassword()));
        userRepository.save(createdUser);
        return modelMapper.map(createdUser, UserResponse.class);
    }
```

Create AuthenticationRequest class in dto.request package

```java
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class AuthenticationRequest {
    String username;
    String password;
}

```

Create AuthenticationResponse class in dto.response package

```java
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class AuthenticationResponse {
    String token;
    boolean isAuthenticated;
}

```

Create AuthenticationService class in service package

```java
@Service
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class AuthenticationService {
    ModelMapper modelMapper;
    UserRepository userRepository;

    @NonFinal
    @Value("${jwt.signerKey}")
    String SIGNER_KEY;
    @NonFinal
    @Value("${jwt.valid-duration}")
    long VALID_DURATION;
    @NonFinal
    @Value("${jwt.refreshable-duration}")
    long REFRESHABLE_DURATION;

    public AuthenticationResponse authenticate(AuthenticationRequest request){
        User user = userRepository.findByUsername(request.getUsername()).orElseThrow(
                () -> new AppException(ErrorCode.USER_NOT_EXISTED)
        );
        PasswordEncoder passwordEncoder = new BCryptPasswordEncoder(5);
        boolean isAuthenticated = passwordEncoder.matches(request.getPassword(), user.getPassword());
        if (!isAuthenticated) throw new AppException(ErrorCode.USER_EXISTED);
        String token = generateToken(user);
        return AuthenticationResponse.builder().token(token).isAuthenticated(true).build();
    }

    /**
     * A JWT include Header, Payload, Signature
     * @param user
     * @return
     */
    public String generateToken(User user){
        JWSHeader header = new JWSHeader(JWSAlgorithm.HS512); // Create the header
        JWTClaimsSet jwtClaimsSet = new JWTClaimsSet.Builder() 
                .subject(user.getUsername())
                .issuer("DL Mocha - Animee")
                .issueTime(new Date())
                .expirationTime(new Date(Instant.now().plus(VALID_DURATION, ChronoUnit.SECONDS).toEpochMilli()))
                .jwtID(UUID.randomUUID().toString())
                .build();

        Payload payload = new Payload(jwtClaimsSet.toJSONObject()); //Create payload using the claimset
        JWSObject jwsObject = new JWSObject(header, payload); //turn header and payload inside one JWS objects
        try{
            jwsObject.sign(new MACSigner(SIGNER_KEY.getBytes())); //sign the JWS object
            return jwsObject.serialize();
        } catch (Exception e){
            throw new RuntimeException(e);
        }
    }

}
```

Create AuthenticationController class in controller package

```java
@RestController
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
@RequestMapping("/auth-service/auth")
public class AuthenticationController {
    AuthenticationService authenticationService;

    @PostMapping("/login")
    public ApiResponse<AuthenticationResponse> login(@RequestBody AuthenticationRequest request){
        ApiResponse<AuthenticationResponse> apiResponse = new ApiResponse<>();
        apiResponse.setResult(authenticationService.authenticate(request));
        return apiResponse;
    }
}

```

### 3. Implement authentication via Oauth2

Spring security consists many security filters, so we need to register a security filter chain in SecurityConfig

Update dependencies in pom.xml

```pom.xml
		<!-- https://mvnrepository.com/artifact/org.springframework.boot/spring-boot-starter-oauth2-resource-server -->
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
			<version>3.3.2</version>
		</dependency>
```

Create SecurityConfig class in config package

```java

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {
    final String PUBLIC_ENDPOINTS[] = {"/auth-service/user", "/auth-service/auth/login", "/auth-service/auth/introspect", " /auth-service/auth/refresh", "/auth-service/auth/logout"};

    @Value("${jwt.signerKey}")
    String SIGNER_KEY;

    @Bean
    SecurityFilterChain filterChain(HttpSecurity httpSecurity) throws Exception{
        httpSecurity.authorizeHttpRequests(
          request -> request.requestMatchers(HttpMethod.POST, PUBLIC_ENDPOINTS).permitAll()
                  .anyRequest().authenticated());

        httpSecurity.oauth2ResourceServer(oauth2 ->
            oauth2.jwt(jwtConfigurer -> jwtConfigurer.decoder(jwtDecoder())));

        httpSecurity.csrf(httpSecurityCsrfConfigurer -> httpSecurityCsrfConfigurer.disable());
        return httpSecurity.build();
    }

    @Bean
    JwtDecoder jwtDecoder(){
        SecretKeySpec secretKeySpec = new SecretKeySpec(SIGNER_KEY.getBytes(), "HS512");
        return NimbusJwtDecoder.withSecretKey(secretKeySpec).macAlgorithm(MacAlgorithm.HS512).build();
    }
}
```
### 4. Create Role and Permission for authorization

Temporary enable all access in Security config .anyRequest().authenticated()

Create Permission and Role in entity packages

```java
@Entity
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@FieldDefaults(level = AccessLevel.PRIVATE)
public class Permission {
    @Id
    String name;
    String description;
}

```


```java
@Entity
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@FieldDefaults(level = AccessLevel.PRIVATE)
public class Role {
    @Id
    String name;
    String description;
    @ManyToMany
    Set<Permission> permissions;
}

```

Create PermissionCreationRequest, RoleCreationRequest, RoleUpdateRequest in dto.request package

```java
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@FieldDefaults(level = AccessLevel.PRIVATE)
public class PermissionCreationRequest {
    String name;
    String description;
}
```

```java
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@FieldDefaults(level = AccessLevel.PRIVATE)
public class RoleCreationRequest {
    String name;
    String description;
    Set<String> permissions;
}

```

```java
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@FieldDefaults(level = AccessLevel.PRIVATE)
public class RoleUpdateRequest {
    String description;
    Set<String> permissions;
}

```

Create PermissionResponse, RoleResponse in dto.response package

```java
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class PermissionResponse {
    String name;
    String description;
}

```

```java
@AllArgsConstructor
@NoArgsConstructor
@Getter
@Setter
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
public class RoleResponse {
    String name;
    String description;
    Set<Permission> permissions;
}

```

Create PermissionRepository, RoleRepository in repository package

```java
@Repository
public interface PermissionRepository extends JpaRepository<Permission, String> {
}
```

```java
@Repository
public interface RoleRepository extends JpaRepository<Role, String> {
}
```

Create PermissionService, RoleService in service package

```java
@Service
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class PermissionService {
    PermissionRepository permissionRepository;
    ModelMapper modelMapper;

    public PermissionResponse createPermission(PermissionCreationRequest request){
        if(permissionRepository.existsById(request.getName())) throw new AppException(ErrorCode.PERMISSION_EXISTED);
        Permission permission = modelMapper.map(request, Permission.class);
        permissionRepository.save(permission);
        return modelMapper.map(permission, PermissionResponse.class);
    }

    public List<PermissionResponse> getAllPermissions(){
        List<Permission> permissions = permissionRepository.findAll();
        return permissions.stream().map(permission -> modelMapper.map(permission, PermissionResponse.class)).toList();
    }

    public void deletePermission(String permissionName){
        Permission foundPermission = permissionRepository.findById(permissionName).orElseThrow(
                () -> new AppException(ErrorCode.PERMISSION_NOT_EXISTED)
        );
        permissionRepository.delete(foundPermission);
    }

}

```java
@Service
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class RoleService {
    RoleRepository roleRepository;
    ModelMapper modelMapper;
    PermissionRepository permissionRepository;

    public RoleResponse createRole(RoleCreationRequest request){
        if(roleRepository.existsById(request.getName())) throw new AppException(ErrorCode.ROLE_EXISTED);
        Role role = modelMapper.map(request, Role.class);
        var permissions = permissionRepository.findAllById(request.getPermissions());
        role.setPermissions(new HashSet<>(permissions));
        roleRepository.save(role);
        return modelMapper.map(role, RoleResponse.class);
    }

    public List<RoleResponse> getAllRoles(){
        List<Role> roles = roleRepository.findAll();
        return roles.stream().map(role -> modelMapper.map(role, RoleResponse.class)).toList();
    }

    public RoleResponse getRole(String roleName){
        Role role = roleRepository.findById(roleName).orElseThrow(
                () -> new AppException(ErrorCode.ROLE_NOT_EXISTED)
        );
        return modelMapper.map(role, RoleResponse.class);
    }

    public RoleResponse updateRole(String roleName, RoleUpdateRequest request){
        Role role = roleRepository.findById(roleName).orElseThrow(
                () -> new AppException(ErrorCode.ROLE_NOT_EXISTED)
        );
        var newPermission = permissionRepository.findAllById(request.getPermissions());
        role.setDescription(request.getDescription());
        role.setPermissions(new HashSet<>(newPermission));
        return modelMapper.map(role, RoleResponse.class);
    }

    public void deleteRole(String roleName){
        Role role = roleRepository.findById(roleName).orElseThrow(
                () -> new AppException(ErrorCode.ROLE_NOT_EXISTED)
        );
        roleRepository.delete(role);
    }
}

```

Create PermissionController, RoleeController in service package

```java
@RestController
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
@RequestMapping("/auth-service/permission")
public class PermissionController {
    PermissionService permissionService;

    @PostMapping
    public ApiResponse<PermissionResponse> createPermission(@RequestBody PermissionCreationRequest request){
        ApiResponse<PermissionResponse> apiResponse = new ApiResponse<>();
        apiResponse.setResult(permissionService.createPermission(request));
        return apiResponse;
    }

    @GetMapping
    public ApiResponse<List<PermissionResponse>> getPermissionDetail(){
        ApiResponse<List<PermissionResponse>> apiResponse = new ApiResponse<>();
        apiResponse.setResult(permissionService.getAllPermissions());
        return apiResponse;
    }

    @DeleteMapping("/{permission}")
    public ApiResponse<PermissionResponse> deletePermission(@PathVariable String permission){
        permissionService.deletePermission(permission);
        return ApiResponse.<PermissionResponse>builder().message("Successfully Deleted!").build();
    }
}

```

```java
@RestController
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
@RequestMapping("/auth-service/role")
public class RoleController {
    RoleService roleService;

    @PostMapping
    public ApiResponse<RoleResponse> createNewRole(@RequestBody RoleCreationRequest request){
        ApiResponse<RoleResponse> apiResponse = new ApiResponse<>();
        apiResponse.setResult(roleService.createRole(request));
        return apiResponse;
    }

    @GetMapping("/{roleName}")
    public ApiResponse<RoleResponse> getRoleDetail(@PathVariable String roleName){
        ApiResponse<RoleResponse> apiResponse = new ApiResponse<>();
        apiResponse.setResult(roleService.getRole(roleName));
        return apiResponse;
    }

    @GetMapping
    public ApiResponse<List<RoleResponse>> getAllRoles(){
        ApiResponse<List<RoleResponse>> apiResponse = new ApiResponse<>();
        apiResponse.setResult(roleService.getAllRoles());
        return apiResponse;
    }

    @PostMapping("/{roleName}")
    public ApiResponse<RoleResponse> updateRole(@PathVariable String roleName, @RequestBody RoleUpdateRequest request){
        ApiResponse<RoleResponse> apiResponse = new ApiResponse<>();
        apiResponse.setResult(roleService.updateRole(roleName, request));
        return apiResponse;
    }

    @DeleteMapping("/{roleName}")
    public ApiResponse<RoleResponse> deleteRole(@PathVariable String roleName){
        roleService.deleteRole(roleName);
        return ApiResponse.<RoleResponse>builder().message(new String("Successfully Deleted!")).build();

    }
}

```
