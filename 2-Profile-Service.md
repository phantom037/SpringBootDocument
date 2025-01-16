
# Spring Boot Profile Service with Neo4J

This project provides cerate and read actions for profile service using Neo4J as databse 

## Features
- **Create Operations**: Create new user profile
- **Read Operations**: Read specific user profile using userId

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
    String userId;
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
    String userId;
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
        System.out.println("request: " + request);
        CharacterProfile characterProfile = modelMapper.map(request, CharacterProfile.class);
        System.out.println("from profile: " + characterProfile);
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

    @GetMapping("/{id}")
    CharacterProfileResponse getCharacter(@PathVariable String id){
        return characterProfileService.getProfile(id);
    }
}

```

Create InternalCharacterProfileController in controller package

```.java
@RestController
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
@RequestMapping("/profile-service")
public class InternalCharacterProfileController {
    CharacterProfileService characterProfileService;

    @PostMapping("/internal")
    public CharacterProfileResponse createCharacter(@RequestBody ProfileCreationRequest request){
        return characterProfileService.createProfile(request);
    }
}
```

