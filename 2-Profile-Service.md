
# Spring Boot Profile Service with Neo4J

This project provides a robust authentication and authorization system for a banking application, featuring JWT-based authentication, role-based access control (RBAC), and CRUD operations for users, roles, and permissions.

## Features

- **JWT-Based Authentication**: Issue JWT tokens and validate them for secure access via OAuth 2.0, allow to validate and refresh token if need.
- **Role-Based Access Control (RBAC)**: Manage roles and permissions for fine-grained access control using filter chain.
- **CRUD Operations**: Manage users, roles, and permissions.
- **Global Exception Handling**: Handles exceptions like `AccessDeniedException`, `AppException`, `MethodArgumentNotValidException`, and more.
- **Custom JWT Decoder**: A scalable JWT decoder that fits into Spring Security’s filter chain for JWT validation and authentication.

## Setup
Intialize Spring boot project with Spring Web, Lombok, Spring Data Neo4j and add ModelMapper

### 1. Create profile entity

Create CharacterProfile class in entity packages

```java
@AllArgsConstructor
@NoArgsConstructor
@Data
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
@Node("character_profile")
public class CharacterProfile {
    @Id
    @GeneratedValue(generatorClass = UUIDStringGenerator.class)
    String id;
    String firstName;
    String lastName;
    LocalDate dob;
    String city;

}

```

Create ProfileCreationRequest in dto.request and CharacterProfileResponse in dto.response

```.java
@AllArgsConstructor
@NoArgsConstructor
@Data
@FieldDefaults(level = AccessLevel.PRIVATE)
public class ProfileCreationRequest {
    String firstName;
    String lastName;
    LocalDate dob;
    String city;
}

```

```.java
@AllArgsConstructor
@NoArgsConstructor
@Data
@FieldDefaults(level = AccessLevel.PRIVATE)
public class CharacterProfileResponse {
    String id;
    String firstName;
    String lastName;
    LocalDate dob;
    String city;
}

```

Create CharacterProfileRepository in repository package

```.java
@Repository
public interface CharacterProfileRepository extends Neo4jRepository<CharacterProfile, String> {
}
```

Create CharacterProfileService in service package

```.java
@Service
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class CharacterProfileService {
    CharacterProfileRepository characterProfileRepository;
    ModelMapper modelMapper;

    public CharacterProfileResponse createProfile(ProfileCreationRequest request){
        CharacterProfile characterProfile = modelMapper.map(request, CharacterProfile.class);
        characterProfileRepository.save(characterProfile);
        return modelMapper.map(characterProfile, CharacterProfileResponse.class);
    }

    public CharacterProfileResponse getProfile(String id){
        CharacterProfile characterProfile = characterProfileRepository.findById(id).orElseThrow(
            () -> new RuntimeException("Profile Not Found"));
        return modelMapper.map(characterProfile, CharacterProfileResponse.class);
    }

}

```

Create CharacterProfileController in controller package

```.java
@RestController
@RequestMapping("/profile-service")
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class CharacterProfileController {
    CharacterProfileService characterProfileService;

    @PostMapping
    CharacterProfileResponse createCharacter(@RequestBody ProfileCreationRequest request){
        return characterProfileService.createProfile(request);
    }

    @GetMapping("/{id}")
    CharacterProfileResponse getCharacter(@PathVariable String id){
        return characterProfileService.getProfile(id);
    }
}

```

