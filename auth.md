+ Create Entity: User
    String id;
    String username;
    String password;
    String firstName;
    String lastName;
    LocalDate dob;

+ Create DTO:
   - Request: UserCreationRequest
                 String username;
                 String password;
                 String firstName;
                 String lastName;
                 LocalDate dob;
     
   - Request: UserUpdateRequest
                 String password;
                 String firstName;
                 String lastName;
                 LocalDate dob;

    - Response: UserResponse
                String id;
                String username;
                String firstName;
                String lastName;
                LocalDate dob;


    - Response: ApiResponse
                int code = 200;
                String message;
                T result;

+ Create Enums: ErrorCode
    int code;
    String message;
    HttpStatus status;

+ Create Error: AppException extends RuntimeException
    ErrorCode errorCode;


+ Create Repository: UserRepository
    boolean existsByUsername(String username);
    Optional<User> findByUsername(String username);

+ Register a bean of ModelMapper in the main class

+ Create Service: UserService
    UserRepository userRepository;
    ModelMapper modelMapper;

+ Create Controller: UserController
    UserService userService;



  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////

+ Create Request: AuthenticationRequest
        String username;
        String password;

+ Create Response: AuthenticationResponse
        String token;
        boolean isAuthenticated;

+ Create Service: AuthenticationService
        ModelMapper modelMapper;
        UserRepository userRepository;

+ Create Controller: AuthenticationController
        AuthenticationService authenticationService;


  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////  ////////
    


  
