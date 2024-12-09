
# Spring Boot Banking Authentication API

This project provides a robust authentication and authorization system for a banking application, featuring JWT-based authentication, role-based access control (RBAC), and CRUD operations for users, roles, and permissions.

## Features

- **JWT-Based Authentication**: Issue JWT tokens and validate them for secure access via OAuth 2.0, allow to validate and refresh token if need.
- **Role-Based Access Control (RBAC)**: Manage roles and permissions for fine-grained access control using filter chain.
- **CRUD Operations**: Manage users, roles, and permissions.
- **Global Exception Handling**: Handles exceptions like `AccessDeniedException`, `AppException`, `MethodArgumentNotValidException`, and more.
- **Custom JWT Decoder**: A scalable JWT decoder that fits into Spring Security’s filter chain for JWT validation and authentication.

## Setup

### 1. Configure Application Properties

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
@Data
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
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
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
@Controller
@RequiredArgsConstructor
@Data
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
    public ApiResponse<UserResponse> createNewUser(UserCreationRequest request){
        ApiResponse<UserResponse> apiResponse = new ApiResponse<>();
        apiResponse.setResult(userService.createUser(request));
        return apiResponse;
    }

    @PostMapping("{id}")
    public ApiResponse<UserResponse> updateUser(@PathVariable String id, @RequestParam UserUpdateRequest request){
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

