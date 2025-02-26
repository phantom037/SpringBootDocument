
# Spring Boot Profile Service with Neo4J

This project provides cerate and read actions for profile service using Neo4J as databse 

## Features
- **Create Operations**: Create new user profile
- **Read Operations**: Read specific user profile using userId

## Setup
Intialize Spring boot project with Spring Web, Lombok, Spring Data Neo4j and add ModelMapper

### 1. Update pom.xml

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
